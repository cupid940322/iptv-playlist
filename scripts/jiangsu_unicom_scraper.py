#!/usr/bin/env python3
"""从恩山论坛帖抓取「江苏联通 OTT 单播」频道列表，生成 jiangsu-unicom.m3u8

来源: https://www.right.com.cn/forum/archiver/tid-8334905.html
（江苏联通 OTT 单播源，南京地区实测可播；JSBC 江苏广电直连，无中转）
"""
import html as html_mod
import os
import re
import sys
import time
import urllib.request

SOURCE_URL = "https://www.right.com.cn/forum/archiver/tid-8334905.html"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

FILTER_RE = re.compile(
    r"VOA|美国之音|自由亚洲|新唐人|希望之声|大纪元", re.IGNORECASE
)


def fetch_page(retries: int = 3) -> str:
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(SOURCE_URL, headers=HEADERS)
            return urllib.request.urlopen(req, timeout=40).read().decode("utf-8", errors="replace")
        except Exception as e:
            last_err = e
            sys.stderr.write(f"请求失败({attempt + 1}/{retries}): {e}\n")
            if attempt < retries - 1:
                time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"数据源不可达: {last_err}")


def parse(text: str) -> list[tuple[str, str]]:
    text = html_mod.unescape(re.sub(r"<[^>]+>", "", text))
    i = text.find("#EXTM3U")
    if i < 0:
        raise ValueError("页面中未找到 #EXTM3U（帖子内容可能变化）")
    pairs, cur = [], None
    for line in text[i:].splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#EXTINF"):
            cur = line
        elif cur and re.match(r"^(https?|rtsp)://", line):
            if not FILTER_RE.search(line):
                pairs.append((cur, line))
            cur = None
    # 按链接去重
    seen, out = set(), []
    for inf, url in pairs:
        if url in seen:
            continue
        seen.add(url)
        out.append((inf, url))
    return out


def main() -> int:
    try:
        pairs = parse(fetch_page())
    except RuntimeError as e:
        if os.path.exists("jiangsu-unicom.m3u8"):
            print(f"WARN: {e}；保留上次结果，本次跳过")
            return 0
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    if not pairs:
        print("WARN: 本次未解析到频道，保留上次结果")
        return 0

    lines = [
        "#EXTM3U",
        f"# 江苏联通 OTT 单播直播源（JSBC 江苏广电直连，无中转；仅限江苏联通网络），更新时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"# 来源: {SOURCE_URL}",
    ]
    lines.extend(f"{inf}\n{url}" for inf, url in pairs)
    content = "\n".join(lines) + "\n"
    for fname in ("jiangsu-unicom.m3u8", "jiangsu-unicom.m3u"):
        with open(fname, "w", encoding="utf-8") as f:
            f.write(content)
    print(f"OK: 共 {len(pairs)} 个频道写入 jiangsu-unicom.m3u8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
