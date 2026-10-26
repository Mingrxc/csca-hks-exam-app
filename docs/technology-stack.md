# 老外1点通项目技术栈说明

整理日期：2026-10-26  
项目版本：1.5.2

项目本体：`D:\Projects\Deng\csca-hks-exam-app`

本文依据当前仓库源码、依赖锁定文件及2026-10-25服务器部署记录整理。前端精确依赖版本取自 `client/package-lock.json`；后端依赖版本取自 `server/requirements.txt`，不代表本次重新检查了服务器安装清单。服务器信息采用既有部署记录。2026-10-26已在本地实现中英界面切换，尚未部署；没有安装新依赖。

## 1. 项目定位与整体架构

老外1点通是面向留学生的 HSK 与 CSCA 学习备考微信小程序，包含题库练习、限时综合练习、错题复习、收藏、学习统计、AI问答、用户反馈和更新公告。

整体采用前后端分离架构：uni-app 编译微信小程序前端，FastAPI 提供单体模块化后端服务，MySQL 保存业务数据，Nginx 提供 HTTPS 入口和题目媒体访问。

```text
微信小程序 / 本地H5预览
        │ HTTPS + JSON + JWT
        ▼
      Nginx
        ├── FastAPI / Uvicorn
        │       ├── SQLAlchemy + PyMySQL → MySQL
        │       ├── HTTPX → 微信登录接口
        │       ├── HTTPX → 阿里云DashScope千问接口
        │       └── ReportLab → 错题PDF
        └── 音频 / 图片静态媒体

原始题库JSON → Python校验/导入工具 → MySQL题目表
```

当前后端按业务模块组织，并非微服务拆分。前端主要交付微信小程序，H5用于本地预览与界面验收；依赖中存在其他uni-app平台包，不表示已发布对应平台产品。

## 2. 前端技术栈

| 分类 | 技术 | 当前锁定版本或用法 |
|---|---|---|
| 应用框架 | uni-app | `3.0.0-alpha-5020220260725001`，Vue3编译链 |
| UI框架 | Vue 3 | `3.5.40`，Composition API、`script setup`、单文件组件 |
| 开发语言 | JavaScript + TypeScript | 源码混合使用JS/TS，页面大量使用`script setup lang="ts"` |
| 状态管理 | Pinia | `2.3.1`，用户身份、备考偏好、答题进度 |
| 界面语言 | 本地轻量 i18n | Vue 响应式词表，简体中文/English，本机记忆、原生导航和 TabBar 更新 |
| 组件库 | TDesign UniApp | `0.10.3`，按钮、图标、标签等 |
| 构建工具 | Vite | `5.2.8`，结合`@dcloudio/vite-plugin-uni` |
| 样式 | SCSS / Sass + CSS变量 | Sass `1.102.0`，共享`--app-*`设计令牌 |
| 转译与压缩 | esbuild | `0.20.2`，生产构建使用esbuild压缩 |
| 包管理 | npm | `package-lock.json`锁定依赖 |
| 小程序路由与导航 | uni-app配置及导航API | `pages.json`、原生导航栏、原生TabBar |
| HTTP与文件下载 | uni-app原生API | 封装`uni.request`、`uni.downloadFile` |
| 本地持久化 | uni-app Storage | 登录令牌、答题快照、AI会话、备考偏好和反馈草稿 |
| 音频与图片 | uni-app原生API | `uni.createInnerAudioContext`、`uni.previewImage` |
| 文档预览 | uni-app原生API | `uni.openDocument`打开错题PDF |

Vue和Pinia等在`package.json`中使用版本范围，上表记录锁定结果。例如Vue声明为`^3.4.21`，当前锁定为`3.5.40`，二者不要混淆。

TypeScript目前由Vue/Vite工具链转译。项目没有单独配置`tsc`类型检查命令，不应把构建成功描述为已完成完整静态类型检查。

### 前端目录与分层

```text
client/src/
├── pages/          页面、路由入口和视图组合
├── components/     题目、答题卡、计时、公共状态等组件
├── features/       领域API和页面级查询逻辑
├── stores/         Pinia跨页面状态
├── api/            统一请求、下载、后端字段转换
├── types/          TypeScript业务类型
├── constants/      考试、品牌、版本等共享常量
├── i18n/           界面语言、词表、原生提示与导航更新
├── shared/         通用组合式逻辑和交互工具
├── styles/         SCSS与全局设计令牌
├── static/         运行图标等静态资源
├── App.vue         应用生命周期
├── main.js         Vue和Pinia初始化
├── pages.json      页面与导航配置
└── manifest.json   小程序配置与应用版本
```

每次构建使用明确的`VITE_API_BASE_URL`。请求层统一处理认证、错误、超时、请求ID和重试；GET网络失败重试一次，写请求不自动进行网络重试，401最多重新登录并重发一次。

当前原生Tab为首页、刷题、AI问答、我的。视觉采用米白背景、陶土主色、浅绿辅助色，通过全局CSS变量统一。

本地代码已支持“我的 → 语言 / Language”切换，题目和用户内容保留原文；AI 问答附加可选 `language: zh/en`，需同步部署后端才能应用新的默认回答语言。没有增加国际化依赖或数据库表。详见 [中英界面切换](interface-language.md)。

1.5.2 定稿公告以 `0009_release_1_5_2` 数据迁移加入现有公告表，执行迁移后可展示，不改数据库结构。此迁移尚未在本次任务中应用到正式库，详见 [1.5.2 发布说明](release-1.5.2.md)。

## 3. 后端技术栈

以下版本为`server/requirements.txt`中的声明版本。

| 分类 | 技术与版本 | 职责 |
|---|---|---|
| 开发语言 | Python | 接口、业务逻辑、导入与维护脚本 |
| Web框架 | FastAPI `0.115.0` | HTTP路由、依赖注入、响应模型、OpenAPI |
| ASGI服务 | Uvicorn `0.30.0` | 运行FastAPI应用 |
| 数据校验 | Pydantic `2.9.0` | 请求/响应模型和字段校验 |
| 配置管理 | pydantic-settings `2.5.0` | 环境变量和本地环境文件 |
| ORM | SQLAlchemy `2.0.35` | 数据模型、查询、关系、连接池和事务 |
| 数据库驱动 | PyMySQL `1.1.1` | 当前实际使用的同步MySQL驱动 |
| 数据库迁移 | Alembic `1.13.0` | 结构版本管理与增量升级 |
| HTTP客户端 | HTTPX `0.27.0` | 调用微信和千问外部接口 |
| JWT | python-jose `3.3.0` | 令牌签发与验证 |
| PDF生成 | ReportLab `4.4.9` | 错题PDF排版与生成 |

数据库访问采用同步SQLAlchemy和PyMySQL，连接字符集为`utf8mb4`。数据库路由使用同步`def`，由FastAPI线程池处理；微信登录交换和AI请求采用异步HTTP I/O。当前不是全异步数据库架构。

### 后端目录与分层

```text
server/
├── main.py                  应用入口
├── src/app.py               应用工厂、中间件、异常处理
├── src/api/v1/router.py     业务路由聚合
├── src/common/              认证、依赖、错误、响应、请求ID、时间工具
├── src/config/              配置与数据库连接
├── src/modules/             业务模块
├── alembic/versions/        数据库迁移
├── tests/                   后端测试
└── requirements.txt         Python依赖声明
```

业务模块内使用`router.py`、`schemas.py`、`service.py`、`models.py`分工。路由负责HTTP与权限，服务层负责业务规则及事务提交，ORM模型负责持久化结构和约束。

### 业务模块

| 模块 | API前缀 | 职责 |
|---|---|---|
| user | `/api/v1/user` | 微信登录、用户资料、目标日期和学习统计 |
| question | `/api/v1/question` | 分类目录、题库查询、组卷与媒体接口 |
| exam | `/api/v1/exam` | 作答、判分、自评、交卷、结果和历史 |
| wrongbook | `/api/v1/wrongbook` | 错题、掌握标记、重做与PDF |
| favorite | `/api/v1/favorite` | 个人收藏 |
| content | `/api/v1/content` | 内容管理与版本更新公告 |
| ai | `/api/v1/ai` | AI文字问答 |
| feedback | `/api/v1/feedback` | 私密反馈及管理员处理 |

业务JSON响应统一使用`code`、`message`、`data`、`request_id`结构。HTTP头`X-Request-ID`用于关联请求与后端日志。PDF和媒体使用对应的文件响应。

## 4. 数据库与题库

| 项目 | 实现 |
|---|---|
| 关系数据库 | MySQL 8.4 LTS；服务器部署记录为`8.4.11` |
| 应用数据库 | `csca_hks_exam` |
| 编码 | `utf8mb4` |
| 结构管理 | Alembic，当前迁移`0008_feedback_announcements` |
| 业务表 | 11张，另有`alembic_version`版本表 |
| 关系约束 | 外键、唯一约束、索引、用户归属过滤 |
| 混合字段 | JSON保存题目选项、原始元数据、试卷题序与筛选配置等 |
| 长文本 | TEXT保存参考答案、文字作答、内容与反馈 |

业务表：

```text
users                  用户
user_exam_targets      分考试目标日期
streak_records         学习打卡
questions              题目
papers                 试卷与练习
answer_records         作答记录
wrong_book             错题记录
knowledge_stats        知识点统计
favorites              收藏
content_items          内容与更新公告
feedback               私密用户反馈
```

原始题库以JSON保存于仓库同级`original_question_bank`，通过Python导入工具校验、转换并写入MySQL。原始题库目录不是数据库文件，也不能代替MySQL服务。

题目以原始`question_id`映射到唯一`bank_id`，支持按稳定题号修订。完整原始元数据保存在服务端`source_data`中。选择题和部分汉字题自动判分，开放表达题保存作答并由用户自评，两类统计口径独立。

当前题库基线为1221题，CSCA550、HSK671；口语与口译99题暂缓，原稿保留。界面显示HSK，既有接口和数据库枚举继续使用内部标识`HKS`。

## 5. AI问答技术栈

| 项目 | 实现 |
|---|---|
| 服务商 | 阿里云DashScope / 百炼兼容接口 |
| 模型配置 | `qwen3.8-27b` |
| 接口协议 | OpenAI兼容的Chat Completions协议 |
| 调用地址 | `https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions` |
| 调用库 | HTTPX AsyncClient |
| 提示词 | 后端构造系统提示词，用户题目和补充材料放在用户消息层 |
| 客户端聊天角色 | user、assistant；客户端不能提交system角色 |
| 当前输入能力 | 文字问题、文字上下文和近期对话 |
| 会话保存 | 客户端本地Storage，当前不是服务端聊天历史库 |

项目通过HTTP直接调用千问，没有使用OpenAI Python SDK。模型由`QWEN_MODEL`配置；兼容协议不变时，更换模型通常通过后端配置和重启完成。

当前AI模块没有接入RAG、向量数据库、联网检索、图像识别、ASR或语音合成。题库听力播放与AI听音识别是不同功能；现有听力题使用题库提供的音频。

## 6. 微信平台能力与媒体

- 身份链路：`uni.login → /user/wx-login → jscode2session → OpenID → 用户记录 → JWT`。
- JWT主体为OpenID，默认有效期72小时，默认算法HS256，生产密钥通过私有配置提供。
- 好友分享使用`onShareAppMessage`，首页朋友圈分享使用`onShareTimeline`；统一品牌图片并支持朋友圈静态预览。
- 头像选择使用微信`chooseAvatar`能力；隐私保护指引入口调用`wx.openPrivacyContract`。
- 目前沿用微信官方隐私授权机制，没有新增自定义隐私授权弹窗。
- 题目音频和图片经HTTPS按需加载，不整体打进小程序主包。
- 生产媒体由Nginx提供白名单静态访问，音频支持Range请求；题目JSON及维护元数据不公开。

## 7. 测试与工程工具

| 分类 | 工具与方式 |
|---|---|
| 后端测试 | pytest `8.3.0` |
| Python异步测试 | pytest-asyncio `0.24.0` |
| API测试 | FastAPI / Starlette TestClient、HTTPX模拟请求 |
| 测试数据库 | 独立SQLite，测试不默认连接正式MySQL |
| 前端测试 | Node.js内置`node:test`和`assert` |
| Vue脚本测试 | Vue SFC编译器、esbuild、Vue响应式、Node VM |
| 版本控制 | Git，当前协作主线为`main` |
| 包体积检查 | Python脚本和构建产物统计 |
| 题库维护 | Python校验、导入、完整性检查、结构导出工具 |
| 部署包 | Python标准库tar/gzip、SHA-256、文件清单 |

最近一次1.5.1验收记录为2026-10-25：后端71项、前端22项通过，微信小程序构建通过；本地H5验收覆盖反馈提交、公告及手机宽度布局。本次整理文档没有重跑业务测试。

`@dcloudio/uni-automator`已列入开发依赖，但不将其列入依赖等同于已建立完整小程序自动化测试或CI流水线。

## 8. 本地环境与生产部署

| 环境 | 当前技术与记录 |
|---|---|
| 本地操作系统 | Windows、PowerShell |
| 本地Python环境 | Conda `deng`，本次核对为Python`3.11.16` |
| 本地Node.js | 本次核对为`v24.21.0`，由npm执行前端脚本 |
| 小程序调试发布 | 微信开发者工具 |
| H5开发预览 | Vite本地开发服务 |
| 云服务器 | 腾讯云上海轻量应用服务器 |
| 服务器操作系统 | 部署记录为Debian`13.7` |
| 服务器Python | 既有虚拟环境，部署记录为Python`3.13.5` |
| HTTPS与反向代理 | Nginx，转发到本机Uvicorn |
| 进程管理 | systemd，后端服务名`laowai-api` |
| 日志 | 应用请求日志及systemd journal |
| 数据库 | 同机MySQL，生产通过回环地址访问 |
| 备份 | SQL备份、配置与代码归档、SHA-256校验，既有定时器执行 |
| 其他运维 | 证书自动续期、健康检查、防火墙、SSH及Fail2ban |

当前采用服务器既有Python环境加systemd运行服务，前端通过微信平台上传、审核和发布。后端上线与小程序发布是两个独立步骤。

本地配置使用`.env`、`.env.local`和前端`.env.*.local`；后端使用pydantic-settings读取，进程环境变量优先。生产配置由服务器私有配置文件及systemd环境文件管理，不能用本机配置覆盖。

反馈及内容管理使用有效JWT，管理员权限由`CONTENT_ADMIN_OPENIDS`白名单控制。业务数据按用户隔离；正式环境关闭开发身份。文档不记录实际密钥、密码或私有OpenID。

## 9. 已声明但非当前核心运行链路的依赖与配置

| 项目 | 声明版本或配置 | 当前状态 |
|---|---|---|
| Redis客户端 | `redis==5.1.0` | 依赖及配置存在，核心业务尚未使用Redis缓存或队列 |
| 异步MySQL驱动 | `aiomysql==0.2.0` | 依赖存在，当前实际数据库链路是同步PyMySQL |
| 密码散列 | `passlib[bcrypt]==1.7.4` | 依赖存在，当前主要登录方式是微信OpenID与JWT |
| 表单/文件解析 | `python-multipart==0.0.12` | 依赖存在，当前反馈为JSON文字提交，不代表已有图片上传链路 |
| 加密依赖 | `cryptography==50.0.1` | requirements声明的加密相关依赖 |
| 对象存储 | OSS配置项 | 预留配置，当前题库媒体实际由服务器本地文件和Nginx提供 |

后续若接入Redis、OSS、录音上传或AI知识库，需要另行实现并验证，不能根据依赖或配置项存在就认定功能已接通。

## 10. 版本与维护依据

- 应用版本：`client/src/manifest.json`，当前`versionName=1.5.1`、`versionCode=151`。
- 前端精确依赖：[package-lock.json](../client/package-lock.json)；依赖声明与命令：[package.json](../client/package.json)。
- 后端依赖声明：[requirements.txt](../server/requirements.txt)。
- 架构约定：[前端架构](frontend-architecture.md)、[后端架构](backend-architecture.md)。
- 题库契约：[question-bank-import-contract.md](question-bank-import-contract.md)。
- 数据库说明：[database/README.md](../database/README.md)。
- 最近发布记录：[release-1.5.1.md](release-1.5.1.md)、[服务器配置记录](server-configuration.md)。

## 11. 可直接复制的简版介绍

```text
老外1点通是一款面向留学生的HSK与CSCA备考微信小程序，采用前后端分离架构。前端使用uni-app、Vue 3、TypeScript/JavaScript、Pinia、TDesign UniApp和SCSS，通过Vite与esbuild构建。后端使用Python、FastAPI、Uvicorn、Pydantic、SQLAlchemy、PyMySQL和Alembic，数据库为MySQL 8.4。微信登录基于OpenID与JWT，AI问答通过HTTPX调用阿里云DashScope的qwen3.8-27b模型，错题PDF由ReportLab生成。题库使用JSON原稿与Python导入工具，音频图片由Nginx经HTTPS提供。服务部署在腾讯云Debian服务器，通过Nginx和systemd管理；测试采用pytest、SQLite和Node.js内置测试工具。本地开发复用Conda deng环境。Redis、异步MySQL驱动和OSS配置目前为预留项。
```
