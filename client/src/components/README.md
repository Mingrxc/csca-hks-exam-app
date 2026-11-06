# 公用组件

答题流程复用 [QuestionItem](QuestionItem/README.md)、[AnswerCard](AnswerCard/README.md) 和 [CountdownBar](CountdownBar/README.md)。[AppState](AppState/README.md) 负责请求状态，[AuthFrame](AuthFrame/README.md) 负责登录边界，[AdminFrame](AdminFrame/README.md) 和 [AdminPager](AdminPager/README.md) 提供管理页容器及分页。

`pages.json` 注册这些组件的 `c-` 标签。[TimelinePreview](TimelinePreview/README.md) 由首页直接导入。
