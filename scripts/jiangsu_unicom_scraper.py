#!/usr/bin/env python3
"""抓取「江苏联通」IPTV 直播源，生成 jiangsu-unicom.m3u8

主源: oyochina/JSLT_iptv —— JSBC 单播 (112.86.202.37:8112，2025-11 更新端口)
备源: lesca/jiangsu-iptv —— 银河 GITV (122.96.52.98:8006，带 Authinfo)
均仅限江苏联通网络。抓取失败时保留上次结果。
"""
import os
import re
import sys
import time
import urllib.request

# gh-proxy 加速优先，回退 GitHub 直连（Actions 环境两种都通）
SOURCES = [
    {
        "name": "JSBC单播",
        "group_prefix": "🇨🇳江苏联通",
        "urls": [
            "https://gh-proxy.com/https://raw.githubusercontent.com/oyochina/JSLT_iptv/main/JSLT.m3u8",
            "https://raw.githubusercontent.com/oyochina/JSLT_iptv/main/JSLT.m3u8",
        ],
        "regroup": True,
    },
    {
        "name": "银河GITV备用",
        "group_prefix": "🇨🇳联通备用",
        "urls": [
            "https://gh-proxy.com/https://raw.githubusercontent.com/lesca/jiangsu-iptv/main/iptv_js_full-latest.m3u",
            "https://raw.githubusercontent.com/lesca/jiangsu-iptv/main/iptv_js_full-latest.m3u",
        ],
        "regroup": False,  # 保留原有分组
    },
]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def fetch_text(urls: list[str], retries: int = 3) -> str:
    """依次尝试多个镜像地址，全部失败抛 RuntimeError"""
    last_err = None
    for url in urls:
        for attempt in range(retries):
            try:
                req = urllib.request.Request(url, headers=HEADERS)
                return urllib.request.urlopen(req, timeout=40).read().decode("utf-8", errors="replace")
            except Exception as e:
                last_err = e
                sys.stderr.write(f"请求失败({attempt + 1}/{retries}) {url[:60]}...: {e}\n")
                if attempt < retries - 1:
                    time.sleep(3)
    raise RuntimeError(f"所有地址均不可达: {last_err}")


def parse_pairs(text: str) -> list[tuple[str, str]]:
    """解析 EXTINF + URL 对"""
    pairs, cur = [], None
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#EXTINF"):
            cur = line
        elif cur and re.match(r"^(https?|rtsp)://", line):
            pairs.append((cur, line))
            cur = None
    return pairs


def guess_group(name: str) -> str:
    if re.search(r"CCTV|CGTN", name, re.IGNORECASE):
        return "央视"
    if "卫视" in name:
        return "卫视"
    if re.search(r"江苏|南京|优漫|卡酷|金鹰|苏州", name):
        return "江苏本地"
    return "其他"


def regroup_inf(inf: str, group: str) -> str:
    """替换/插入 group-title"""
    inf = re.sub(r'\s*group-title="[^"]*"', "", inf)
    parts = inf.split(",")
    return parts[0].rstrip() + f' group-title="{group}",' + parts[-1]


def main() -> int:
    blocks = []
    total = 0
    had_success = False
    for src in SOURCES:
        try:
            text = fetch_text(src["urls"])
            pairs = parse_pairs(text)
        except RuntimeError as e:
            if src["name"] == "JSBC单播" and not os.path.exists("jiangsu-unicom.m3u8"):
                print(f"ERROR: {e}", file=sys.stderr)
                return 1
            print(f"WARN: {src['name']} 抓取失败，跳过。原因: {e}")
            continue
        if not pairs:
            print(f"WARN: {src['name']} 未解析到频道，跳过")
            continue
        had_success = True
        seen = set()
        kept = 0
        for inf, url in pairs:
            if url in seen:
                continue
            seen.add(url)
            name = inf.split(",")[-1].strip()
            if src["regroup"]:
                group = f'{src["group_prefix"]}-{guess_group(name)}'
            else:
                orig = re.search(r'group-title="([^"]*)"', inf)
                group = f'{src["group_prefix"]}-{orig.group(1) if orig else "其他"}'
            inf = regroup_inf(inf, group)
            blocks.append((inf, url))
            kept += 1
        sys.stderr.write(f"{src['name']}: 保留 {kept} 个频道\n")
        total += kept

    if total == 0:
        print("WARN: 本次未获取到任何频道，保留上次结果")
        return 0
    if not had_success:
        return 0

    lines = [
        "#EXTM3U",
        f"# 江苏联通 IPTV 直播源（仅限江苏联通网络），更新时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "# 分组1: JSBC单播(112.86.202.37:8112 直连) | 分组2: 银河GITV备用(122.96.52.98:8006)",
    ]
    for inf, url in blocks:
        lines.append(inf)
        lines.append(url)
    content = "\n".join(lines) + "\n"
    for fname in ("jiangsu-unicom.m3u8", "jiangsu-unicom.m3u"):
        with open(fname, "w", encoding="utf-8") as f:
            f.write(content)
    print(f"OK: 共 {total} 个频道写入 jiangsu-unicom.m3u8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
