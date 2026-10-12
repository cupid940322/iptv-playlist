#!/usr/bin/env python3
"""从 epg.51zmt.top 组播地址库抓取江苏省频道，生成 jiangsu-multicast.m3u8"""
import json
import re
import sys
import time
import urllib.request

BASE = "https://epg.51zmt.top:8001"
INDEX_URL = BASE + "/multicast/"
PROVINCE = "江苏省"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": INDEX_URL,
}


def http_get(url: str, timeout: int = 40) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", errors="replace")


def extract_regions(html: str) -> dict:
    """从页面提取内嵌的 regionsData（省份 -> 源列表）"""
    key = "const regionsData = "
    i = html.find(key)
    if i < 0:
        print("ERROR: 页面中未找到 regionsData", file=sys.stderr)
        sys.exit(1)
    seg = html[i + len(key):]
    depth, end = 0, None
    for j, ch in enumerate(seg):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = j + 1
                break
    if end is None:
        print("ERROR: regionsData 解析失败", file=sys.stderr)
        sys.exit(1)
    return json.loads(seg[:end])


def fetch_channels(source_id: int) -> tuple[dict, list]:
    body = http_get(f"{BASE}/multicast/api/channels/{source_id}/")
    data = json.loads(body)
    if not data.get("success"):
        print(f"ERROR: 源 {source_id} 获取失败", file=sys.stderr)
        sys.exit(1)
    return data.get("source", {}), data.get("channels", [])


def main():
    regions = extract_regions(http_get(INDEX_URL))
    sources = regions.get(PROVINCE, [])
    if not sources:
        print(f"ERROR: 未找到 {PROVINCE} 的组播源", file=sys.stderr)
        sys.exit(1)
    sys.stderr.write(f"{PROVINCE} 源数量: {len(sources)}\n")

    lines = [
        "#EXTM3U",
        f"# 江苏省组播地址（来源: 老张的EPG epg.51zmt.top），更新时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "# 若播放器不支持 rtp:// 协议，可将 rtp:// 替换为 udp://@",
    ]
    total = 0
    for src in sources:
        sid = src["id"]
        sname = src.get("name", f"source{sid}")
        meta, channels = fetch_channels(sid)
        sys.stderr.write(f"  {sname}(id={sid}): {len(channels)} 个频道\n")
        group = f"🇨🇳{sname}组播"
        for c in channels:
            url = (c.get("rtp_url") or "").strip()
            if not url:
                addr = (c.get("multicast_address") or "").strip()
                if not addr:
                    continue
                url = "rtp://" + addr
            name = (c.get("channel_name") or "").strip()
            if not name:
                continue
            lines.append(f'#EXTINF:-1 tvg-name="{name}" group-title="{group}",{name}')
            lines.append(url)
            total += 1

    if total == 0:
        print("ERROR: 未抓取到任何频道", file=sys.stderr)
        sys.exit(1)

    content = "\n".join(lines) + "\n"
    for fname in ("jiangsu-multicast.m3u8", "jiangsu-multicast.m3u"):
        with open(fname, "w", encoding="utf-8") as f:
            f.write(content)
    print(f"OK: 共 {total} 个频道写入 jiangsu-multicast.m3u8")


if __name__ == "__main__":
    main()
