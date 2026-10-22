# 新版题库导入与应用契约

更新：2026-10-22。内部 HSK 标识继续使用 HKS；原始题库位于仓库同级 original_question_bank。

## 本批范围

原始库共1320题：CSCA550、HSK3.0 770。按用户确认，暂缓94道口语与5道口译，原稿及素材保留。首版导入1221题：CSCA550、HSK671。

- CSCA五科各110题；HSK一级110、二级110、三级至六级各90、七至九级联合91题。
- 1115道选择题及25道汉字题自动校验，81道开放表达题自评。本批全部按模拟题管理。
- 活动题引用94份音频和59张图片，素材经HTTP(S)加载，不进入小程序包。

## 字段与身份

原始 question_id 映射到唯一 bank_id；接口 id 仍为整数主键。题干、答案或知识点修订不改变同一稳定题号的数据库身份。

独立持久化 exam_version、level、knowledge_module、material_id、response_mode、scoring_mode、max_score。options[].image 完整保留。answer 和用户作答均为TEXT。source_data保存完整原始记录，包括来源、审核状态、难度依据、原文、评分量表、图表数值和翻译方向；该JSON不直接暴露给客户端。

同编号内容冲突、缺必需素材、缺解析或分类不合法会阻止写入。--apply新增或更新，不自动删除源外旧记录；本批按用户确认在备份后重建库，避免新旧题混入。

## 组卷与作答

- HSK必须显式选择HSK3.0和等级1至6或7-9；CSCA不使用HSK等级。
- 分类按科目／考试模块、知识模块、知识点筛选，按共享材料保持完整题组；日常练习返回实际题量。
- real策略界面名称为“限时综合练习”，按等级配置非口语模块练习配比。这是产品练习配置，不是官方完整试卷；材料或题量不足会明确报错。
- 练习和考试组卷均不提前下发答案内容、解析、原文、可接受答案和评分要点。练习提交后返回solution，考试交卷后返回完整复习信息。
- 单选核验有效选项；只有多选忽略顺序。汉字题保留字符顺序并使用明确的可接受答案。
- written_response、essay、short_answer、translation保存原作答，is_correct=NULL，状态awaiting_self_review。用户对照参考答案和量表自评，保存self_score和self_reviewed，不自动判错或加入错题本。
- 累计完成数包含开放题，正确率分母只包含自动判分题，成绩与历史口径一致。纯开放题显示自评，不显示为0%正确率；作答保存UTC，今日统计与打卡按北京时间划日。

## 接口和媒体

- GET /question/catalog：实际可用的版本、等级、科目、模块、知识点与题数。
- POST /question/generate-paper：新增examVersion、level、subjects、knowledgeModules；knowledgePoints为细分知识点。
- POST /exam/submit：练习提交后返回solution与评阅状态。
- POST /exam/self-review：本人已提交的开放题可记录0至max_score的自评分；考试必须先交卷。
- GET /question/media/{relative}：仅提供HSK/_assets下允许的音频和图片；阻止目录穿越、题目JSON和.meta.json。

QUESTION_BANK_ROOT默认指向仓库同级原始题库，可按服务器目录覆盖。QUESTION_MEDIA_BASE_URL为空时走本项目媒体接口，设置为HTTPS前缀时可改用独立媒体托管。不要把整个原始目录直接公开为静态网站。

## 初始化与验证

复用现有Conda deng环境，不安装新依赖。项目根目录执行：

```powershell
python scripts/import_questions.py
python scripts/reset_database.py
python scripts/reset_database.py --apply --expected-database csca_hks_exam
python scripts/check_database_integrity.py
cd server
python -m alembic check
python -m pytest -q
```

reset_database默认只输出计划。实际执行先成功生成SQL备份与SHA-256，再重建业务表和Alembic状态，升级到0007_question_bank_v2并导入题库；不更改MySQL服务、账号或真实配置。非本地主机另需显式--allow-remote。

后续题目修订用import_questions.py --apply。export_schema.py从ORM生成结构参考；正式初始化使用Alembic。build_backend_bundle.py包含新版后端、迁移、题目及活动题实际引用的153个媒体文件，不含真实环境配置、备份或用户数据。保留包内相对目录。

本地验收不代表已经发布。音频播放验证不代替逐条人工听审。开放题自评不是官方评分或AI评阅。
