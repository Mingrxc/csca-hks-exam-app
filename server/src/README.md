# 后端源码

`app.py` 创建 FastAPI 应用，安装异常处理、跨域、请求日志和健康接口，并挂载 [API](api/README.md)。请求经 [modules](modules/README.md) 的路由进入领域服务，数据库会话和环境配置在 [config](config/README.md)，共用鉴权和响应在 [common](common/README.md)。
