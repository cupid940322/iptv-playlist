#!/usr/bin/env python3
"""同步「江苏移动 IPTV 直播源」(cicivi/jsyd-iptv)，生成 jiangsu-mobile.m3u8

上游: https://github.com/cicivi/jsyd-iptv （江苏移动魔百盒 ott.mobaibox.com 直连，
含央视/卫视/江苏省内/NewTV/4K8K/广播，作者高频维护）。仅限江苏移动网络。
"""
import os
import re
import sys
import time
import urllib.request

MIRRORS = [
    "https://gh-proxy.com/https://raw.githubusercontent.com/cicivi/jsyd-iptv/main/m3u/iptv.m3u8",
    "https://testingcf.jsdelivr.net/gh/cicivi/jsyd-iptv/m3u/iptv.m3u8",
    "https://cdn.jsdelivr.net/gh/cicivi/jsyd-iptv/m3u/iptv.m3u8",
    "https://raw.githubusercontent.com/cicivi/jsyd-iptv/main/m3u/iptv.m3u8",
]
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

FILTER_WORDS = ("VOA", "美国之音", "自由亚洲", "新唐人", "希望之声", "大纪元")


def fetch(retries: int = 3) -> str:
    last_err = None
    for url in MIRRORS:
        for attempt in range(retries):
            try:
                req = urllib.request.Request(url, headers=HEADERS)
                return urllib.request.urlopen(req, timeout=40).read().decode("utf-8", errors="replace")
            except Exception as e:
                last_err = e
                sys.stderr.write(f"请求失败({attempt + 1}/{retries}) {url[:55]}...: {e}\n")
                if attempt < retries - 1:
                    time.sleep(3)
    raise RuntimeError(f"所有镜像均不可达: {last_err}")


def main() -> int:
    try:
        text = fetch()
    except RuntimeError as e:
        if os.path.exists("jiangsu-mobile.m3u8"):
            print(f"WARN: 上游暂不可用，保留上次结果，本次跳过。原因: {e}")
            return 0
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    if not text.startswith("#EXTM3U"):
        print(f"WARN: 上游返回异常内容，保留上次结果。开头: {text[:100]!r}")
        return 0

    # 逐行过滤敏感频道（成对处理 EXTINF 与其后的 URL）
    out, skip = [], False
    kept = 0
    epg_url = ""
    for line in text.splitlines():
        if line.startswith("#EXTM3U"):
            m = re.search(r'x-tvg-url="([^"]+)"', line)
            if m:
                epg_url = m.group(1)
            continue
        if line.startswith("#EXTINF"):
            skip = any(w.lower() in line.lower() for w in FILTER_WORDS)
            if not skip:
                out.append(line)
                kept += 1
            continue
        if line.startswith("#"):
            if not skip:
                out.append(line)
            continue
        if line.strip():
            if not skip:
                out.append(line)
        else:
            skip = False

    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    header = "#EXTM3U"
    if epg_url:
        header += f' x-tvg-url="{epg_url}"'
    header += (
        "\n"
        f"# 江苏移动 IPTV 直播源（魔百盒直连，仅限江苏移动网络），更新时间: {stamp}\n"
        "# 上游: github.com/cicivi/jsyd-iptv\n"
    )
    content = header + "\n".join(out).lstrip("\n") + "\n"

    for fname in ("jiangsu-mobile.m3u8", "jiangsu-mobile.m3u"):
        with open(fname, "w", encoding="utf-8") as f:
            f.write(content)
    print(f"OK: 共 {kept} 个频道写入 jiangsu-mobile.m3u8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
