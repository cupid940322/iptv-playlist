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

### 3. iptv-search 中国地方台（约 614 个）

```
https://raw.githubusercontent.com/cupid940322/iptv-playlist/main/china-local.m3u8
```

加速链接：

```
https://gh-proxy.com/https://raw.githubusercontent.com/cupid940322/iptv-playlist/main/china-local.m3u8
```

或 jsDelivr CDN：

```
https://cdn.jsdelivr.net/gh/cupid940322/iptv-playlist@main/china-local.m3u8
```

来自 [iptv-search.com](https://iptv-search.com./category/%E4%B8%AD%E5%9B%BD%E5%9C%B0%E6%96%B9%E5%8F%B0) 的「中国地方台」分类，覆盖全国各地市/县级地方频道（经站方代理转链）。

### 4. 江苏省组播地址（204 个）

```
https://raw.githubusercontent.com/cupid940322/iptv-playlist/main/jiangsu-multicast.m3u8
```

加速链接：

```
https://gh-proxy.com/https://raw.githubusercontent.com/cupid940322/iptv-playlist/main/jiangsu-multicast.m3u8
```

或 jsDelivr CDN：

```
https://cdn.jsdelivr.net/gh/cupid940322/iptv-playlist@main/jiangsu-multicast.m3u8
```

来自 [老张的EPG 组播地址库](https://epg.51zmt.top:8001/multicast/) 的江苏省数据（江苏电信组播），共 204 个频道。地址为 `rtp://IP:端口` 格式：

- **仅能在对应的运营商网络内播放**（需光猫 LAN 侧组播可达，通常配合 IPTV 机顶盒所在网络）
- 若播放器不支持 `rtp://`，可将地址前缀 `rtp://` 替换为 `udp://@`

### 5. 江苏联通 OTT 单播（104 个，江苏联通用户推荐）

```
https://raw.githubusercontent.com/cupid940322/iptv-playlist/main/jiangsu-unicom.m3u8
```

加速链接：

```
https://gh-proxy.com/https://raw.githubusercontent.com/cupid940322/iptv-playlist/main/jiangsu-unicom.m3u8
```

或 jsDelivr CDN：

```
https://cdn.jsdelivr.net/gh/cupid940322/iptv-playlist@main/jiangsu-unicom.m3u8
```

JSBC 江苏广电**直连单播**（`112.86.202.37` / `122.97.211.133`），无中转跳数，延迟低；含央视、卫视、江苏各地市频道。**仅限江苏联通网络**播放；个别频道为 `rtsp://` 协议，VLC / PotPlayer 可直接播放。

### 6. 江苏移动 IPTV（210 个）

```
https://raw.githubusercontent.com/cupid940322/iptv-playlist/main/jiangsu-mobile.m3u8
```

加速链接：

```
https://gh-proxy.com/https://raw.githubusercontent.com/cupid940322/iptv-playlist/main/jiangsu-mobile.m3u8
```

或 jsDelivr CDN：

```
https://cdn.jsdelivr.net/gh/cupid940322/iptv-playlist@main/jiangsu-mobile.m3u8
```

来自 [cicivi/jsyd-iptv](https://github.com/cicivi/jsyd-iptv)（高频维护），魔百盒 `ott.mobaibox.com` 直连，含央视/卫视/江苏省内/NewTV/4K8K/广播。**仅限江苏移动网络**播放。

## 自动更新说明

| 文件 | 数据来源 | 更新时间（北京时间） |
|------|----------|----------------------|
| `result.m3u8` / `result.m3u` | Guovin/iptv-api 官方 | 每天 9:17 |
| `china.m3u8` / `china.m3u` | eja.tv 中国区 | 每天 9:47 |
| `china-local.m3u8` / `china-local.m3u` | iptv-search.com 中国地方台 | 每天 10:07 |
| `jiangsu-multicast.m3u8` / `.m3u` | 老张的EPG 江苏组播 | 每天 10:37 |
| `jiangsu-unicom.m3u8` / `.m3u` | 恩山论坛 江苏联通 OTT 单播 | 每天 11:07 |
| `jiangsu-mobile.m3u8` / `.m3u` | cicivi/jsyd-iptv 江苏移动 | 每天 11:27 |

- 内容无变化时自动跳过提交；每次提交记录均带数据时间戳
- 可在 Actions 页面手动触发 Run workflow 立即更新

## 说明

- `result.m3u8` 文件头部附带 EPG 节目单地址，支持频道预告
- `china.m3u8` 由 [scripts/eja_scraper.py](scripts/eja_scraper.py) 抓取生成
- `china-local.m3u8` 由 [scripts/iptvsearch_scraper.py](scripts/iptvsearch_scraper.py) 抓取生成
- `jiangsu-multicast.m3u8` 由 [scripts/jiangsu_multicast_scraper.py](scripts/jiangsu_multicast_scraper.py) 抓取生成
- `jiangsu-unicom.m3u8` 由 [scripts/jiangsu_unicom_scraper.py](scripts/jiangsu_unicom_scraper.py) 抓取生成
- `jiangsu-mobile.m3u8` 由 [scripts/jiangsu_mobile_scraper.py](scripts/jiangsu_mobile_scraper.py) 同步生成
- 更新记录见提交历史
