# 小程序前端

`package.json` 定义微信小程序的开发、构建及定向测试命令，`package-lock.json` 锁定依赖。`vite.config.js` 配置 uni-app 插件和 `@` 源码别名，构建后从静态资源产物里移除目录说明。微信项目从 `src/manifest.json` 读取 AppID 和版本。

页面与领域代码见 [src](src/README.md)，回归用例见 [tests](tests/README.md)。按构建模式从 [.env.example](.env.example) 配置 API 地址，具体路径和校验步骤见[根目录说明](../README.md)。
