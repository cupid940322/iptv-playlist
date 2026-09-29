#!/usr/bin/env python3
"""从 iptv-search.com 抓取「中国地方台」分类频道并生成 china-local.m3u8

原理：页面内嵌全部频道数据（name/hash/logo/group），播放链接为固定格式
https://iptv-search.com/live/fav/<token>/<hash>，token 全局固定，
通过 /api/play/link 接口动态获取，避免 token 变化导致失效。
"""
import html as html_mod
import json
import re
import sys
import time
import urllib.request
import uuid

SITE = "https://iptv-search.com"
CATEGORY_PATH = "/category/%E4%B8%AD%E5%9B%BD%E5%9C%B0%E6%96%B9%E5%8F%B0"  # 中国地方台
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

# 过滤不适合分发的频道（名称正则，忽略大小写）
FILTER_RE = re.compile(
    r"VOA|美国之音|自由亚洲|新唐人|希望之声|大纪元|DW\s?德国之声", re.IGNORECASE
)


def http_get(url: str, headers: dict | None = None, timeout: int = 40) -> str:
    req = urllib.request.Request(url, headers=headers or HEADERS)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", errors="replace")


def fetch_channels() -> list[dict]:
    """抓取分类页面，提取内嵌频道数组并去重、过滤"""
    html = http_get(SITE + CATEGORY_PATH)
    m = re.search(r"var channels = (\[.*?\]);", html, re.DOTALL)
    if not m:
        print("ERROR: 页面中未找到频道数据", file=sys.stderr)
        sys.exit(1)
    channels = json.loads(m.group(1))
    seen, uniq = set(), []
    for c in channels:
        h = c.get("hash")
        if not h or h in seen:
            continue
        name = html_mod.unescape((c.get("name") or "").strip())
        if not name or FILTER_RE.search(name):
            continue
        seen.add(h)
        uniq.append({"hash": h, "name": name, "logo": (c.get("logo") or "").strip(), "group": "中国地方台"})
    return uniq


def get_token() -> str:
    """请求一个频道的播放链接，从中提取全局 token"""
    first = channels_cache[0]["hash"]
    body = http_get(
        f"{SITE}/api/play/link?hash={first}",
        headers={"X-Fingerprint": uuid.uuid4().hex, "User-Agent": HEADERS["User-Agent"], "Referer": SITE + "/"},
    )
    data = json.loads(body)
    link = data.get("play_link", "")
    m = re.search(r"/live/fav/([A-Za-z0-9]+)/", link)
    if not data.get("success") or not m:
        print(f"ERROR: 获取播放 token 失败: {body[:200]}", file=sys.stderr)
        sys.exit(1)
    return m.group(1)


channels_cache: list[dict] = []


def main():
    global channels_cache
    channels_cache = fetch_channels()
    sys.stderr.write(f"页面去重后频道数: {len(channels_cache)}\n")
    token = get_token()
    sys.stderr.write(f"播放 token: {token}\n")

    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "#EXTM3U",
        f"# 抓取自 iptv-search.com 中国地方台，更新时间: {stamp}",
    ]
    for c in channels_cache:
        attrs = f'tvg-name="{c["name"]}"'
        if c["logo"]:
            attrs += f' tvg-logo="{c["logo"]}"'
        lines.append(f'#EXTINF:-1 {attrs} group-title="🇨🇳中国地方台",{c["name"]}')
        lines.append(f"{SITE}/live/fav/{token}/{c['hash']}")

    content = "\n".join(lines) + "\n"
    for fname in ("china-local.m3u8", "china-local.m3u"):
        with open(fname, "w", encoding="utf-8") as f:
            f.write(content)
    print(f"OK: 共 {len(channels_cache)} 个频道写入 china-local.m3u8")


if __name__ == "__main__":
    main()
