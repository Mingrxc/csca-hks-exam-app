param(
  [ValidateSet('quick', 'named', 'token')]
  [string]$Mode = 'quick',
  [string]$PublicUrl = $env:CLOUDFLARE_PUBLIC_URL,
  [string]$TunnelName = $env:CLOUDFLARE_TUNNEL_NAME,
  [string]$TunnelToken = $env:CLOUDFLARE_TUNNEL_TOKEN,
  [string]$PythonPath = $env:CSCA_PYTHON_PATH,
  [switch]$StartWatcher
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ServerRoot = Join-Path $ProjectRoot 'server'
$ClientRoot = Join-Path $ProjectRoot 'client'
$RuntimeRoot = Join-Path $ServerRoot '.dev'
$ToolsRoot = Join-Path $ServerRoot 'tools'

function Find-ProjectPython {
  $candidates = @(
    $PythonPath,
    (Join-Path $env:USERPROFILE 'miniforge3\envs\deng\python.exe')
  )
  if ($env:CONDA_DEFAULT_ENV -eq 'deng') {
    $activePython = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($activePython) {
      $candidates = @($activePython.Source) + $candidates
    }
  }
  foreach ($candidate in $candidates) {
    if ($candidate -and (Test-Path -LiteralPath $candidate)) {
      return (Resolve-Path -LiteralPath $candidate).Path
    }
  }
  throw 'Python for Conda environment deng was not found. Activate deng or set CSCA_PYTHON_PATH.'
}

$Python = Find-ProjectPython

function Find-Cloudflared {
  $candidates = @(
    $env:CLOUDFLARED_PATH,
    (Join-Path $ToolsRoot 'cloudflared.exe'),
    (Join-Path $env:TEMP 'cloudflared.exe')
  )

  foreach ($candidate in $candidates) {
    if ($candidate -and (Test-Path -LiteralPath $candidate)) {
      return (Resolve-Path -LiteralPath $candidate).Path
    }
  }

  $command = Get-Command cloudflared.exe -ErrorAction SilentlyContinue
  if ($command) {
    return $command.Source
  }

  throw 'cloudflared was not found. Install it manually, then set CLOUDFLARED_PATH or add it to PATH.'
}

function Test-BackendHealth {
  try {
    $response = Invoke-WebRequest -UseBasicParsing -TimeoutSec 3 -Uri 'http://127.0.0.1:8000/api/v1/health'
    return $response.StatusCode -eq 200
  } catch {
    return $false
  }
}

function Test-BackendReady {
  try {
    $response = Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 -Uri 'http://127.0.0.1:8000/api/v1/content/home'
    return $response.StatusCode -eq 200
  } catch {
    return $false
  }
}

function Test-TcpPort([int]$port) {
  $client = New-Object System.Net.Sockets.TcpClient
  try {
    $task = $client.ConnectAsync('127.0.0.1', $port)
    if (-not $task.Wait(1500)) {
      return $false
    }
    return $client.Connected
  } catch {
    return $false
  } finally {
    $client.Dispose()
  }
}

function Start-Database {
  if (Test-TcpPort 3306) {
    Write-Host 'MySQL is ready on port 3306.' -ForegroundColor DarkCyan
    return
  }

  $service = @(
    Get-Service -Name 'MySQL84', 'MySQL80' -ErrorAction SilentlyContinue
  ) | Sort-Object { if ($_.Name -eq 'MySQL84') { 0 } else { 1 } } | Select-Object -First 1
  if (-not $service) {
    throw 'Neither MySQL84 nor MySQL80 was found and port 3306 is unavailable.'
  }

  if ($service.Status -ne 'Running') {
    try {
      Start-Service -Name $service.Name
    } catch {
      $command = "Start-Service -Name '$($service.Name)'"
      $encodedCommand = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($command))
      try {
        $elevated = Start-Process -FilePath 'powershell.exe' -Verb RunAs -Wait -PassThru -WindowStyle Hidden -ArgumentList @(
          '-NoProfile',
          '-ExecutionPolicy',
          'Bypass',
          '-EncodedCommand',
          $encodedCommand
        )
        if ($elevated.ExitCode -ne 0) {
          throw 'The elevated MySQL start command failed.'
        }
      } catch {
        throw "$($service.Name) is stopped. Start it manually, then run this script again."
      }
    }
  }

  $deadline = (Get-Date).AddSeconds(30)
  while ((Get-Date) -lt $deadline) {
    if (Test-TcpPort 3306) {
      Write-Host 'MySQL is ready on port 3306.' -ForegroundColor Green
      return
    }
    Start-Sleep -Milliseconds 500
  }

  throw "$($service.Name) did not become ready on port 3306. Check the MySQL service log."
}

function Start-Backend {
  if (Test-BackendReady) {
    Write-Host 'Backend is already running on port 8000.' -ForegroundColor DarkCyan
    return
  }

  if (-not (Test-BackendHealth)) {
    if (-not (Test-Path -LiteralPath $Python)) {
      throw "Missing project Python: $Python"
    }

    New-Item -ItemType Directory -Force -Path $RuntimeRoot | Out-Null
    $stdout = Join-Path $RuntimeRoot 'uvicorn.out.log'
    $stderr = Join-Path $RuntimeRoot 'uvicorn.err.log'
    $arguments = @('-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000', '--reload')
    Start-Process -FilePath $Python -ArgumentList $arguments -WorkingDirectory $ServerRoot -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr | Out-Null
  }

  $deadline = (Get-Date).AddSeconds(30)
  while ((Get-Date) -lt $deadline) {
    if (Test-BackendReady) {
      Write-Host 'Backend is ready on http://127.0.0.1:8000.' -ForegroundColor Green
      return
    }
    Start-Sleep -Milliseconds 500
  }

  throw "Backend did not become ready. Check $stderr"
}

function Get-TunnelLog {
  $parts = @()
  foreach ($file in @(
    (Join-Path $RuntimeRoot 'cloudflared.out.log'),
    (Join-Path $RuntimeRoot 'cloudflared.err.log')
  )) {
    if (Test-Path -LiteralPath $file) {
      $parts += Get-Content -LiteralPath $file -Raw -ErrorAction SilentlyContinue
    }
  }
  return ($parts -join "`n")
}

function Start-Tunnel([string]$cloudflared) {
  New-Item -ItemType Directory -Force -Path $RuntimeRoot | Out-Null
  $stdout = Join-Path $RuntimeRoot 'cloudflared.out.log'
  $stderr = Join-Path $RuntimeRoot 'cloudflared.err.log'
  Set-Content -LiteralPath $stdout -Value '' -Encoding UTF8
  Set-Content -LiteralPath $stderr -Value '' -Encoding UTF8

  if ($Mode -eq 'named') {
    if (-not $TunnelName) {
      throw 'Named mode requires CLOUDFLARE_TUNNEL_NAME or -TunnelName.'
    }
    if (-not $PublicUrl) {
      throw 'Named mode requires CLOUDFLARE_PUBLIC_URL or -PublicUrl.'
    }
    $arguments = @('tunnel', '--no-autoupdate', 'run', $TunnelName)
    Start-Process -FilePath $cloudflared -ArgumentList $arguments -WorkingDirectory $ServerRoot -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr | Out-Null
    return $PublicUrl.TrimEnd('/')
  }

  if ($Mode -eq 'token') {
    if (-not $TunnelToken) {
      throw 'Token mode requires CLOUDFLARE_TUNNEL_TOKEN or -TunnelToken.'
    }
    if (-not $PublicUrl) {
      throw 'Token mode requires CLOUDFLARE_PUBLIC_URL or -PublicUrl.'
    }
    $arguments = @('tunnel', '--no-autoupdate', 'run', '--token', $TunnelToken)
    Start-Process -FilePath $cloudflared -ArgumentList $arguments -WorkingDirectory $ServerRoot -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr | Out-Null
    return $PublicUrl.TrimEnd('/')
  }

  $arguments = @('tunnel', '--no-autoupdate', '--protocol', 'http2', '--url', 'http://127.0.0.1:8000')
  Start-Process -FilePath $cloudflared -ArgumentList $arguments -WorkingDirectory $ServerRoot -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr | Out-Null

  $deadline = (Get-Date).AddSeconds(45)
  while ((Get-Date) -lt $deadline) {
    $content = Get-TunnelLog
    $match = [regex]::Match($content, 'https://[a-z0-9-]+\.trycloudflare\.com')
    if ($match.Success) {
      return $match.Value.TrimEnd('/')
    }
    Start-Sleep -Milliseconds 500
  }

  throw "Cloudflare Quick Tunnel did not provide a public URL. Check $stderr"
}

function Wait-PublicApi([string]$apiBaseUrl) {
  $endpoint = "$apiBaseUrl/content/home"
  $deadline = (Get-Date).AddSeconds(30)
  while ((Get-Date) -lt $deadline) {
    try {
      $response = Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 -Uri $endpoint
      if ($response.StatusCode -eq 200) {
        return
      }
    } catch {}

    # Some local DNS providers cache a newly issued Quick Tunnel hostname late.
    # Resolve through a public DNS server and use curl's --resolve for the probe.
    try {
      $uri = [Uri]$endpoint
      $addresses = @(
        Resolve-DnsName -Name $uri.Host -Type A -Server '1.1.1.1' -ErrorAction Stop |
          Where-Object { $_.IPAddress } |
          Select-Object -ExpandProperty IPAddress -Unique
      )
      foreach ($address in $addresses) {
        $resolveTarget = "$($uri.Host):$($uri.Port):$address"
        & curl.exe -k -sS --max-time 5 --resolve $resolveTarget $endpoint -o NUL 2>$null
        if ($LASTEXITCODE -eq 0) {
          return
        }
      }
    } catch {}
    Start-Sleep -Milliseconds 500
  }
  throw "Public API is not ready: $endpoint"
}

function Update-FrontendEnv([string]$apiBaseUrl) {
  $files = @(
    (Join-Path $ClientRoot '.env.development.local'),
    (Join-Path $ClientRoot '.env.production.local')
  )
  foreach ($file in $files) {
    $lines = @()
    if (Test-Path -LiteralPath $file) {
      $lines = @(Get-Content -LiteralPath $file)
    }
    $lines = @($lines | Where-Object {
      $_ -notmatch '^VITE_API_BASE_URL=' -and
      $_ -notmatch '^VITE_API_FALLBACK_URL=' -and
      $_ -notmatch '^VITE_API_TIMEOUT_MS='
    })
    $lines += "VITE_API_BASE_URL=$apiBaseUrl"
    $lines += 'VITE_API_TIMEOUT_MS=15000'
    Set-Content -LiteralPath $file -Value $lines -Encoding UTF8
  }
}

function Build-Frontend {
  Push-Location $ClientRoot
  try {
    & npm.cmd run build:mp-weixin
    if ($LASTEXITCODE -ne 0) {
      throw 'Frontend build failed.'
    }
  } finally {
    Pop-Location
  }
}

$cloudflared = Find-Cloudflared
Start-Database
Start-Backend
$publicOrigin = Start-Tunnel $cloudflared
$apiBaseUrl = "$publicOrigin/api/v1"
Wait-PublicApi $apiBaseUrl
Update-FrontendEnv $apiBaseUrl
Build-Frontend

Write-Host ''
Write-Host "Public API: $apiBaseUrl" -ForegroundColor Green
Write-Host 'Mini Program build: client\dist\build\mp-weixin' -ForegroundColor Green
Write-Host "Tunnel logs: $RuntimeRoot\cloudflared.*.log" -ForegroundColor DarkCyan

if ($StartWatcher) {
  $watchStdout = Join-Path $RuntimeRoot 'uni-watch.out.log'
  $watchStderr = Join-Path $RuntimeRoot 'uni-watch.err.log'
  Start-Process -FilePath 'npm.cmd' -ArgumentList @('run', 'dev:mp-weixin') -WorkingDirectory $ClientRoot -WindowStyle Hidden -RedirectStandardOutput $watchStdout -RedirectStandardError $watchStderr | Out-Null
  Write-Host "Watcher logs: $RuntimeRoot\uni-watch.*.log" -ForegroundColor DarkCyan
}
