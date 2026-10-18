# 腾讯云首次部署进度

记录日期：2026-10-21，Asia/Shanghai。

用户于 10 月 21 日返回，要求先验证可自主连接和操作服务器，再正式开始部署。目前连接验证已完成，尚未开始后续生产配置，没有安排提醒或自动化。
10 月 19 日的安装由用户在腾讯云 OrcaTerm 中执行；10 月 21 日已通过直接 SSH 独立核实下列访问能力及部分环境状态。

## 自主访问已验证（2026-10-21）

- 使用本机现有 Conda `deng` 环境中的 Paramiko，通过 SSH 连接 `deploy@43.142.125.251:22`，服务器主机名为 `VM-4-10-debian`。
- 已验证普通用户身份、sudo 提权、`sudo mysql` 管理连接、SFTP 临时文件写入/读取/删除，以及关闭连接后重新建立独立连接。
- MySQL 服务为 `active`，版本 `8.4.11`；2GB Swap 仍启用；服务器 Python 为 `3.13.5`，`pip check` 输出 `No broken requirements found.`。
- 本机仅在现有 `deng` 环境安装 Paramiko `5.1.0`、Invoke `3.0.3`、PyNaCl `1.6.2`，保留原有 cryptography/bcrypt/cffi 版本，未安装全局软件或修改系统 Python。
- 访问凭据由用户填写在项目工作区外层 `.deployment-access` 下的受限文件，后续只在程序内读取，经 SSH 标准输入传给 sudo，禁止打印或提交。该目录忽略 Git 跟踪；非敏感验证结果在 `access-check-report.json`。
- 使用保存的 SSH 主机密钥严格校验后续连接。首次密钥为首次连接接受，并非通过腾讯云控制台独立核对。
- 用户确认电脑保持开机、联网；自主 SSH 操作不依赖 OrcaTerm 页面，也无需用户逐条输入命令。耗时任务仍应按需使用 tmux 或 systemd，避免依赖单次终端连接。
- 目前仅完成访问验证与部署前检查，未修改部署配置或写入业务数据库。用户已填写受限本机文件 `.deployment-access/production-credentials.txt`，提供数据库密码、微信 AppID/AppSecret 和通义千问 API Key，禁止在输出或文档中记录其值。

## 凭据与域名预检查（2026-10-21）

- 用户明确此次先沟通，尚未正式启动生产部署。服务器配置及业务数据均未修改。
- 提供的 MySQL 应用密码已通过 SSH 上的真实 TCP 连接验证；账号 `laowai_app@127.0.0.1`，数据库 `csca_hks_exam`，表数为 0，当前具备迁移所需 DDL 权限。
- AppID 格式符合；AppSecret 在去除意外首尾空白后符合格式，部署读取时只对这类令牌字段去除首尾空白，不擅自修剪数据库或 SSH 密码。微信凭据尚未通过真实微信登录验证。
- 凭据文件第 17 行有一条非 `KEY=VALUE` 的额外中文内容，属于非配置内容；读取凭据只接收明确列出的四个字段，不把额外内容当作密钥或可执行指令。
- 从服务器使用提供的 Qwen Key 查询 `https://dashscope.aliyuncs.com/compatible-mode/v1/models`，返回 HTTP 200 和模型列表；未调用付费生成。代码默认 `qwen-plus-2025-07-28` 未出现在返回列表，正式部署时需确定可用模型并验证，不能据此单独断言该模型不可调用。
- 本机 DNS 返回 `198.18.0.x` 代理地址，因此以服务器查询为准：主域名和 `www` 均指向 `43.142.125.251`。用户随后在轻量服务器控制台新增了 `api` 的 A 记录；已通过服务器 `getent ahostsv4 api.laowaiyidiantong.icu` 独立确认解析为 `43.142.125.251`，API 子域名 DNS 已就绪。控制台新增成功弹窗中的“设置 HTTPS”是后续操作入口，不代表证书或 HTTPS 已配置。
- 用户只要求本次完成服务器部署；微信后台合法域名、小程序生产配置及微信真机联调由用户自行完成。服务端仍应预先配置已提供的微信凭据并关闭开发登录。

## 已确认的部署决策

- 使用现有腾讯云上海轻量应用服务器，公网 IPv4：`43.142.125.251`。
- 用户确认域名 ICP 备案、小程序备案均已完成，正式微信 AppID 和 AppSecret 已准备好。
- 基础域名：`laowaiyidiantong.icu`，已有 `www` 域名记录。
- 计划使用 `https://api.laowaiyidiantong.icu/api/v1` 作为 API 地址；该子域名的 DNS、证书和微信合法域名配置尚未进行。
- 线上只导入题库，用户和答题记录从零开始，不迁移本地数据库业务记录。
- 计划采用 Nginx + FastAPI/Uvicorn + systemd + 本机 MySQL，Redis 当前不必运行。

## 服务器已完成

- 2 核 CPU、约 2GB RAM、40GB 系统盘，套餐为 3Mbps、每月 200GB 流量。
- Debian 从 13.2 更新到 13.7，已重启；内核 `6.12.113+deb13-amd64`，架构 `x86_64`。
- 时区 `Asia/Shanghai`，NTP 同步正常。
- `/swapfile` 为 2GB，已添加 `/etc/fstab` 启动配置；备份文件 `/etc/fstab.before-miniapp-swap`。10 月 21 日已通过 SSH 确认重启后 Swap 仍为 2GB、启用中。
- 已安装基础工具、tmux、Python 3 和 python3-venv。
- 已创建 Linux 用户 `deploy`，属于 `sudo` 组，已验证 `sudo whoami` 输出 `root`。
- 腾讯云防火墙原有 TCP 22、TCP 80、ICMP，用户确认新增允许公网 IPv4 访问 TCP 443。未开放公网 3306、33060 或 8000。
- 22 端口规则及 root 登录方式尚未收紧；后续先验证其他管理登录途径，再调整登录策略。

## MySQL 已完成

- 官方 APT 仓库选择 `mysql-8.4-lts`，安装包版本 `8.4.11-1debian13`。
- 服务已验证 `active (running)`、`enabled`；使用 `sudo mysql` 本机管理。
- 配置文件 `/etc/mysql/mysql.conf.d/99-laowai.cnf`：

```ini
[mysqld]
bind-address=127.0.0.1
mysqlx-bind-address=127.0.0.1
innodb_dedicated_server=OFF
innodb_buffer_pool_size=256M
max_connections=40
```

- SQL 查询已确认地址、缓存和连接数生效，`ss` 已确认 3306、33060 只监听 `127.0.0.1`。
- 已创建数据库 `csca_hks_exam`，字符集 `utf8mb4`，排序规则 `utf8mb4_0900_ai_ci`。
- 应用账号 `laowai_app@127.0.0.1`，通过本机 TCP、密码交互输入的连接测试已成功。
- 初始化阶段提供的项目库权限为 `SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX, REFERENCES`。完成 Alembic 初始化后应撤销运行账号不需要的 DDL 权限，并明确后续迁移授权流程。
- 未执行 Alembic，也未正式导入题库；项目库仍待初始化。
- 用户已通过受限本机凭据文件提供 MySQL 应用密码，并已验证可连接；文档和聊天不记录任何密码。

## 后端部署包与运行环境

- 本地打包工具：`D:\Projects\Deng\deployment-artifacts\build_backend_bundle.py`。
- 部署包：`D:\Projects\Deng\deployment-artifacts\laowai-backend-20261019.tar.gz`，248663 字节。
- SHA-256：`5d07421317cdb8976020c2e5aa85d830499e57741fc2d71326b37571d89f69a7`。
- 部署包是显式允许列表构建，包含后端源码、测试、6 个 Alembic 迁移、两个题库工具、28 个原始题库 JSON，以及不含真实凭据的环境模板。
- 包中不含真实 `.env` / `.env.local`、数据库导出、用户答题记录、前端依赖、媒体二进制文件或 Git 元数据。
- 用户已上传到 `/home/deploy/laowai-backend-20261019.tar.gz`，服务器 SHA-256 校验为 OK。
- 解压目录 `/opt/laowai`，归 `deploy` 管理。
- 后端：`/opt/laowai/csca-hks-exam-app/server`。
- 项目脚本：`/opt/laowai/csca-hks-exam-app/scripts`。
- 原始题库：`/opt/laowai/original_question_bank`，已确认 28 个 JSON。
- Python 虚拟环境：`/opt/laowai/csca-hks-exam-app/server/.venv`，Python `3.13.5`，初始 pip `25.1.1`。
- 依赖安装命令使用 `.venv/bin/python -m pip install --only-binary=:all: --timeout 60 --retries 3 -r requirements.txt`；没有更改项目锁定的直接依赖版本。
- 服务器测试结果已确认 `40 passed, 2 warnings in 1.13s`。警告来自 Starlette/AnyIO 的旧接口和 python-jose 的 `datetime.utcnow()` 弃用，不是测试失败。
- 10 月 21 日已通过 SSH 执行 `pip check`，结果为 `No broken requirements found.`。
- 题库 dry run 已确认：1876 题，CSCA 265、HKS 1611；跳过源重复 14 条、非题目语法资源 8 条，均与本地基线一致。最后提示 `Dry run only`，没有写入数据库。
- 当前生产环境文件尚未创建或填写。包内有 `server/.env.production.example`，可作为后续模板。
- 用户在结束当天工作时澄清：今天的操作均在普通终端中执行，不能假定存在可恢复的 `mysql-install` tmux 会话。已展示的安装、测试和预检查均已结束；断开普通终端不会撤销已保存的文件、配置或已完成的安装，MySQL 由 systemd 独立管理。
- 之前一次浏览器断线留下 MySQL 安装密码窗口，指导用户针对确认的旧进程组 6299 发送 SIGTERM 后恢复安装，最终已确认 MySQL 安装成功；不要再次操作旧 PID 或删除锁文件。

## 下次从这里继续

1. 用户正式开始部署后，使用已验证的直接 SSH 通道，以 `deploy` 身份进入 `/opt/laowai/csca-hks-exam-app/server`。后续交互长任务可用 `tmux new -A -s deploy-setup` 明确创建或接入会话，不要假定已有会话。Swap 和 `pip check` 已确认正常，无须重复作为阻塞步骤。
2. 使用用户已填写的受限本机凭据文件，在服务器配置生产环境文件与权限。数据库主机固定 `127.0.0.1`，用户名 `laowai_app`；生成新的随机 JWT 密钥，凭据不能输出到聊天、命令参数或提交仓库。
3. 必须明确设置 `APP_ENV=production` 和 `AUTH_ALLOW_DEV_OPENID=false`。现有代码不会因为 production 模式自动禁用模拟登录。
4. 新库执行 `.venv/bin/python -m alembic upgrade head`，验证到 `0006_ownership_foreign_keys`。不要使用旧 `schema.sql` 或 `alembic stamp` 跳过迁移。
5. 按脚本先 dry run、再 `--apply`，随后执行 `--verify-db` 和 `check_database_integrity.py`，检查表、外键和 1876 题。初始化完成后收紧应用账号权限。
6. 设置非 root 运行的 systemd 服务，首先只监听 `127.0.0.1:8000`，启动后验证健康检查与数据库相关接口。Nginx 和 FastAPI 服务当前均未配置或发布。
7. 完成 API 子域名 DNS、Nginx、HTTPS 证书与自动续期。微信 request/downloadFile 合法域名及真实微信登录联调按用户最新分工交由用户完成，交付时提供准确的配置清单。
8. 处理题库媒体：497 道题的音频使用第三方 `media.mandarinzone.com` HTTPS 链接；60 道图片题中 45 个为 `www.mandarinzone.com` HTTP 链接，15 个为 `/test/.../img/...` 相对路径。媒体未随部署包上传，需确认来源、落实 HTTPS 地址并真机验证。
9. 用户已提供 Qwen Key，实际模型调用尚未验收；默认前端超时 15 秒、后端 Qwen 超时 45 秒，需向用户交付超时配置建议或在明确授权范围内处理，服务器部署不自动扩大为前端改动。
10. 向用户交付小程序生产环境地址、正式 AppID 和域名校验配置说明，由用户完成构建发布及真实登录、组卷答题、错题、音频图片、PDF 等真机验收。
11. 配置数据库备份、日志轮转、恢复与回滚流程，再完成上线验收。

服务尚未发布。测试通过表示已验证服务器运行环境与现有测试覆盖的逻辑，不等同于正式微信登录、真实 MySQL 迁移或完整小程序功能已验收。
