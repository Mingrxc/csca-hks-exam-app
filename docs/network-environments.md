# Network and Runtime Environments

The mini-program uses exactly one API origin per build. It never guesses between local and public backends.

| Environment | API example | Intended use |
|---|---|---|
| Local WeChat DevTools | `http://127.0.0.1:8000/api/v1` | Normal local development |
| LAN device | `http://192.168.x.x:8000/api/v1` | Controlled same-network testing |
| Temporary HTTPS | `https://temporary.example/api/v1` | Short-lived remote device testing |
| Production | `https://api.example.com/api/v1` | Stable released mini-program |

Set the selected value in `.env.development.local` or `.env.production.local` as appropriate. Production builds fail when `VITE_API_BASE_URL` is absent. A production release must not use localhost, a raw LAN address, or an expired temporary tunnel.

## Request policy

- Default timeout: 15 seconds, configurable through `VITE_API_TIMEOUT_MS`.
- Network retry: one retry for GET only.
- POST, PUT, and DELETE: never retried automatically.
- A 401 clears the current session. Subsequent private actions use the explicit login flow.
- Errors: normalized into `ApiRequestError` with status, application code, and request ID when available.
- Correlation: every HTTP request sends `X-Request-ID`; backend logs and error responses return the same value.

## Diagnosing `request fail`

1. Open `http://127.0.0.1:8000/api/v1/health` on the development machine.
2. Confirm the active mode-local environment file contains the expected single API origin.
3. Restart the uni-app build after changing environment files.
4. For a phone, remember that `127.0.0.1` points to the phone, not the development computer.
5. For LAN testing, bind Uvicorn to `0.0.0.0`, use the computer's LAN address, and verify the Windows firewall rule deliberately.
6. For a public mini-program, configure a stable HTTPS request domain in the WeChat console. Register the same host separately as an uploadFile domain for avatars.
7. Use the request ID shown in client logs to find the matching backend request.

## Optional public-development script

`scripts/start_public_dev.ps1` is optional. It requires the existing Conda `deng` Python environment, npm, MySQL, and an already-installed `cloudflared` binary. The script never downloads tools. It discovers `MySQL84` before the legacy `MySQL80`, removes obsolete fallback variables, and writes one API origin to both local mode files for the generated build.

Set `CSCA_PYTHON_PATH` or `CLOUDFLARED_PATH` in the shell when the installed executables are outside the standard locations. Named mode requires `CLOUDFLARE_PUBLIC_URL` and `CLOUDFLARE_TUNNEL_NAME`. Token mode requires `CLOUDFLARE_PUBLIC_URL` and `CLOUDFLARE_TUNNEL_TOKEN`. The default quick mode obtains a temporary address from cloudflared.

Local development does not require a public server or tunnel. Production requires a reachable HTTPS backend, but that backend may be a VM, container platform, serverless service, or another stable deployment target.
