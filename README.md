# IPTV 直播源自动更新

基于 [Guovin/iptv-api](https://github.com/Guovin/iptv-api) 官方每日生成的播放列表，由 GitHub Actions 每天早上 9:00（北京时间）自动拉取最新版本并提交到本仓库。

## 使用

将以下任一链接导入播放器（PotPlayer / VLC / TiviMate / DIYP 等）：

```
https://raw.githubusercontent.com/cupid940322/iptv-playlist/main/result.m3u8
```

国内网络推荐使用加速链接（速度快、更稳定）：

```
https://gh-proxy.com/https://raw.githubusercontent.com/cupid940322/iptv-playlist/main/result.m3u8
```

或 jsDelivr CDN：

```
https://cdn.jsdelivr.net/gh/cupid940322/iptv-playlist@main/result.m3u8
```

## 说明

- `result.m3u8` / `result.m3u`：最新播放列表（约 1100+ 频道，含央视、卫视、地方频道）
- 文件头部附带 EPG 节目单地址，支持频道预告
- 更新记录见提交历史；每次提交的 commit message 中带有官方数据的时间戳
