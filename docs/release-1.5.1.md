# 1.5.1 代码更新与发布准备

更新：2026-10-25。代码已提交为f5ae203b，正式服务器已完成1.5.1部署及0008增量迁移。复用既有Conda和服务器Python环境，没有安装依赖；微信小程序由用户另行上传和发布。

本次已备份并保留原有34用户、18份试卷、44条答题、21条错题及其余全部旧记录，迁移后原字段内容逐表校验一致。备份位于 `/var/backups/laowai/before-v1.5.1-20261025-220540`。正式健康版本1.5.1，反馈、公告隐藏和实际AI回复验收通过。迁移新增的公告仍为未发布草稿；管理员白名单未擅自设置。下文“本轮没有执行MySQL”等描述为最初代码维护阶段记录，当前状态以此段和服务器配置文档为准。

## 已确定范围

- AI 学习助手去除旧品牌，优化讲题和复习建议。系统规则只由后端控制，题目与上下文留在用户消息层；客户端不能传 `system` 角色。
- “我的”新增纯文字用户反馈：题目问题、功能异常、使用建议、其他；私密提交，运营者读取，不公开留言。
- “关于”仅包含品牌图标、名称、版本 `1.5.1`、简短介绍、更新公告和隐私保护指引。反馈入口单独放在“我的”，关于中不增加联系入口或题库/AI适用说明。
- 沿用微信官方隐私授权机制，不新增自定义弹窗、不改启动登录流程。隐私保护指引入口只调用 `wx.openPrivacyContract`；微信后台隐私声明由运营者按实际处理信息完善。

## 数据库：只做增量迁移

新迁移 `0008_feedback_announcements` 基于 `0007_question_bank_v2`：新增 `feedback` 表，给 `content_items` 增加 `release_version`、`published_at`。原有题库、用户、练习、错题、收藏与统计保留。

本轮没有执行现有 MySQL 或正式数据库迁移。测试使用独立 SQLite，并验证迁移保留已有记录；另已生成 MySQL 离线迁移 SQL。

正式部署时先用现有流程备份，确认当前迁移版本，再在既有服务器 Python 环境执行：

```text
cd /opt/laowai/csca-hks-exam-app/server
python -m alembic current
python -m alembic upgrade head
python -m alembic current
python -m alembic check
```

本次更新不使用 `reset_database.py`，不重建数据库、不重新导入题库。先升级数据库和后端，再发布匹配的 `1.5.1` 小程序。迁移至新表前不要启用新版后端；代码回退时可保留新增字段和表，避免丢失反馈。

## 用户反馈

- `POST /api/v1/feedback`：登录用户提交；正文去首尾空白后为 1–1000 字，分类受限，客户端不能指定用户ID。
- `GET /api/v1/feedback/admin?status=unread&page=1&page_size=20`：管理员分页读取，单页最多100条。
- `PUT /api/v1/feedback/admin/{id}/status`：管理员将状态设为 `unread`、`read` 或 `resolved`。
- 用户提交只收到编号、状态与时间。没有公开反馈列表，也没有普通用户读取他人反馈的接口。
- 反馈及内容管理使用有效 JWT；即使本地开发身份开启，缺少令牌也不能匿名进入这些接口。管理员复用 `CONTENT_ADMIN_OPENIDS` 白名单，正式配置必须填写实际运营账号，不将私有OpenID写入仓库。
- `(user_id, request_id)` 唯一，网络失败后原样重试返回同一编号；相同key改内容返回409。当前限制同用户30秒内一条、北京时间每日20条；重试已有提交不消耗次数。
- 草稿按用户ID保存在 `feedback_draft_v1_{userId}`；发送期间不能重复提交或改写，失败保留草稿和幂等key，成功后清理并显示回执。反馈正文不写入业务访问日志。

有服务器访问权限的运营者可直接使用现有后端环境读取：

```text
python scripts/manage_feedback.py --status unread
python scripts/manage_feedback.py --page 2 --page-size 50
python scripts/manage_feedback.py --mark 12 --to read
python scripts/manage_feedback.py --mark 12 --to resolved
```

以上从项目根目录运行。默认只读；只有 `--mark` 配合 `--to` 才改变状态。`--output` 可将当前页导出到指定的仓库外私有 JSON 路径，反馈内容及导出文件不得提交Git。

## 更新公告

复用已有内容管理页面 `/pages/content-admin/index` 及后台内容接口，不在普通用户的“关于”增加管理入口。

管理员编辑通知，启用“作为更新公告展示”，填写版本号、标题、摘要与正文。关闭“发布展示”保存草稿；开启后发布，首次发布由服务端记录UTC时间，客户端按北京时间显示日期。已有接口也支持未来的 `published_at`，到时前不可公开读取。

公开列表 `GET /api/v1/content/announcements`，详情 `GET /api/v1/content/announcements/{id}`；列表分页，只有已启用、版本信息完整且已到发布时间的更新公告可见。通用内容详情也不能绕过下线或未来发布时间限制。公告正文用纯文本显示，不执行HTML。

迁移准备一份 `1.5.1 更新说明` 草稿，默认不公开。版本正式发布后，运营者核对内容再启用。没有公告时页面显示真实空状态，不用演示内容填充；原先读取空内容库自动插入演示资讯的逻辑已移除，不自动删除现有内容。

## 版本与验证

`client/src/manifest.json` 为界面展示的版本来源，`versionName=1.5.1`、`versionCode=151`；package/lock根版本及后端API版本同步为 `1.5.1`。微信开发者工具上传版本同样填写 `1.5.1`。

```text
# 使用现有 Conda deng，server目录
python -m pytest -q
python -m alembic upgrade 0007_question_bank_v2:head --sql

# client目录
npm run test:ai
npm run test:bank
npm run test:profile
npm run build:mp-weixin
```

本地已验证AI消息边界、私密反馈权限/重试/限额、公告发布/撤下/草稿隐藏、迁移保留旧数据、页面草稿恢复及提交回执。微信实际隐私指引打开效果和真机键盘仍需正式配置下验收；本轮没有调用付费AI。
