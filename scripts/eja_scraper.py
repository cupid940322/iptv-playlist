#!/usr/bin/env python3
"""从 eja.tv 抓取中国区频道并生成 china.m3u8"""
import html as html_mod
import re
import sys
import time
import urllib.request
import urllib.parse

# 过滤不适合分发的频道（名称正则，忽略大小写）
FILTER_RE = re.compile(
    r"VOA|美国之音|自由亚洲|新唐人|希望之声|大纪元|DW\s?德国之声", re.IGNORECASE
)

BASE = "https://eja.tv/"
STEP = 6
MAX_OFFSET = 300  # 安全上限

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

NAME_RE = re.compile(
    r'<h5 class="card-title">\s*<span class="text-muted">(.*?)</span>', re.DOTALL
)
SRC_RE = re.compile(r'<source src="([^"\s]+?)(?:#([a-f0-9]{64}))?"')
OFFSET_RE = re.compile(r"offset=(\d+)")
CARD_SPLIT = '<div class="card h-100">'


def fetch_page(offset: int) -> str:
    params = urllib.parse.urlencode(
        {"offset": offset, "country": "cn", "language": "", "category": "", "search": ""}
    )
    req = urllib.request.Request(BASE + "?" + params, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def strip_tags(s: str) -> str:
    return html_mod.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def extract_cards(html: str):
    """按卡片块解析，返回 [(频道名, 播放地址)]"""
    items = []
    seen = set()
    for block in html.split(CARD_SPLIT)[1:]:
        m_name = NAME_RE.search(block)
        m_src = SRC_RE.search(block)
        if not m_name or not m_src:
            continue
        name = strip_tags(m_name.group(1))
        url = m_src.group(1)
        if not name or not url.startswith(("http://", "https://")):
            continue
        if url in seen:
            continue
        if FILTER_RE.search(name):
            continue
        seen.add(url)
        items.append((name, url))
    return items


def main():
    all_channels = []
    offset = 0
    while offset <= MAX_OFFSET:
        html = fetch_page(offset)
        cards = extract_cards(html)
        if not cards:
            break
        all_channels.extend(cards)
        sys.stderr.write(f"offset={offset}: +{len(cards)} (累计 {len(all_channels)})\n")
        next_offsets = [int(x) for x in OFFSET_RE.findall(html)]
        candidates = [x for x in next_offsets if x > offset]
        if not candidates:
            break
        offset = min(candidates)

    if not all_channels:
        print("ERROR: 未抓取到任何频道", file=sys.stderr)
        sys.exit(1)

    lines = [
        "#EXTM3U",
        f"# 抓取自 eja.tv 中国区，更新时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
    ]
    for name, url in all_channels:
        lines.append(f'#EXTINF:-1 tvg-name="{name}" group-title="🇨🇳EJA中国频道",{name}')
        lines.append(url)

    content = "\n".join(lines) + "\n"
    for fname in ("china.m3u8", "china.m3u"):
        with open(fname, "w", encoding="utf-8") as f:
            f.write(content)

    print(f"OK: 共 {len(all_channels)} 个频道写入 china.m3u8")


if __name__ == "__main__":
    main()
