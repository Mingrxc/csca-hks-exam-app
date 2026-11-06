# 小程序源码

`main.js` 创建 Vue 和 Pinia，`App.vue` 在启动时初始化语言、恢复登录态，并在退到后台时保存练习进度。`pages.json` 定义页面、原生标签栏和 easycom 组件，`manifest.json` 维护微信构建元数据。

改功能时从 [pages](pages/README.md) 找页面，经 [features](features/README.md) 的领域请求和状态逻辑调用 [api](api/README.md)。跨页状态由 [stores](stores/README.md) 保存，登录、查询状态和确认对话框等共用逻辑放在 [shared](shared/README.md)。组件和样式入口见 [components](components/README.md) 与 [styles](styles/README.md)。
