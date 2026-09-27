# IPTV 直播源自动更新

基于 [Guovin/iptv-api](https://github.com/Guovin/iptv-api) 官方每日生成的播放列表，由 GitHub Actions 每天早上 9:00（北京时间）自动拉取最新版本并提交到本仓库。

同时抓取 [eja.tv](https://eja.tv/?country=cn) 中国区频道，每天早上 9:30（北京时间）自动更新。

## 使用

### 1. 综合播放列表（约 1100+ 频道）

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

### 2. eja.tv 中国频道（约 54 个）

```
https://raw.githubusercontent.com/cupid940322/iptv-playlist/main/china.m3u8
```

加速链接：

```
https://gh-proxy.com/https://raw.githubusercontent.com/cupid940322/iptv-playlist/main/china.m3u8
```

或 jsDelivr CDN：

```
https://cdn.jsdelivr.net/gh/cupid940322/iptv-playlist@main/china.m3u8
```

包含 CGTN 系列、CCTV+、湖南卫视国际版、浙江卫视国际、广州 TV 及各地方频道等。

## 自动更新说明

| 文件 | 数据来源 | 更新时间（北京时间） |
|------|----------|----------------------|
| `result.m3u8` / `result.m3u` | Guovin/iptv-api 官方 | 每天 9:00 |
| `china.m3u8` / `china.m3u` | eja.tv 中国区 | 每天 9:30 |

- 内容无变化时自动跳过提交；每次提交记录均带数据时间戳
- 可在 Actions 页面手动触发 Run workflow 立即更新

## 说明

- `result.m3u8` 文件头部附带 EPG 节目单地址，支持频道预告
- `china.m3u8` 由 [scripts/eja_scraper.py](scripts/eja_scraper.py) 抓取生成
- 更新记录见提交历史
