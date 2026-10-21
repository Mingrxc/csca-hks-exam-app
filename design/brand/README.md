# 品牌图标原稿

`icon-original.png` 是原始 1254 × 1254 PNG 图标，完整保留原始文件，供后续设计或重新导出使用。

小程序实际使用 `client/src/static/brand/icon.png`，为同一设计的 384 × 384 PNG，约 140 KiB。原稿位于前端源码目录之外，不随小程序代码包发布。

好友分享、朋友圈分享和朋友圈预览通过 `client/src/constants/brand.ts` 的 `APP_ICON_PATH` 统一引用运行图片。修改资源后，应检查构建产物中的媒体大小和主包体积，并进行真机分享验收。
