#!/usr/bin/env python3
"""
verify_urls.py — 批量验证 raw URL 是否可访问

用途：检查 scripts/url-list.txt 里的每个 raw URL 是否能正常访问。
    避免文件名编码、删除、移动导致 404，确保 ima 批量入库能成功。

用法：
    python scripts/verify_urls.py                            # 默认验证 scripts/url-list.txt
    python scripts/verify_urls.py --input urls.txt           # 自定义输入文件
    python scripts/verify_urls.py --timeout 10               # 自定义超时（秒）

输出：
    控制台进度条 + 最终统计（OK / Failed 数量 + 失败 URL 列表）

依赖：
    Python 3.6+（仅标准库 urllib）
"""

import argparse
import re
import sys
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


def parse_url_list(file_path: Path) -> list:
    """解析 url-list.txt，跳过注释行（以 # 开头）"""
    urls = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            urls.append(line)
    return urls


def verify_url(url: str, timeout: int = 10) -> tuple:
    """验证单个 URL 可访问性，返回 (url, status_code, message)"""
    try:
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return (url, resp.status, 'OK')
    except urllib.error.HTTPError as e:
        return (url, e.code, f'HTTP Error: {e.reason}')
    except urllib.error.URLError as e:
        return (url, None, f'URL Error: {e.reason}')
    except Exception as e:
        return (url, None, f'Error: {type(e).__name__}: {e}')


def main():
    parser = argparse.ArgumentParser(
        description="批量验证 raw URL 是否可访问",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        '--input', default='scripts/url-list.txt',
        help='URL 列表文件路径（默认 scripts/url-list.txt）',
    )
    parser.add_argument(
        '--timeout', type=int, default=10,
        help='单 URL 超时秒数（默认 10）',
    )
    parser.add_argument(
        '--workers', type=int, default=10,
        help='并发线程数（默认 10）',
    )
    parser.add_argument(
        '--failed-only', action='store_true',
        help='只输出失败的 URL（默认输出全部）',
    )

    args = parser.parse_args()

    # 脚本所在目录
    script_dir = Path(__file__).parent
    input_path = script_dir.parent / args.input

    if not input_path.exists():
        print(f"❌ 输入文件不存在：{input_path}", file=sys.stderr)
        print(f"   先跑 python scripts/gen_urls.py 生成 URL 列表", file=sys.stderr)
        sys.exit(1)

    urls = parse_url_list(input_path)
    if not urls:
        print(f"❌ URL 列表为空：{input_path}", file=sys.stderr)
        sys.exit(1)

    print(f"🔍 验证 {len(urls)} 个 URL（超时 {args.timeout}s，并发 {args.workers}）...")
    print()

    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_url = {executor.submit(verify_url, url, args.timeout): url for url in urls}

        for i, future in enumerate(as_completed(future_to_url), 1):
            url, status, msg = future.result()
            results.append((url, status, msg))

            # 进度显示
            symbol = '✅' if status == 200 else '❌'
            print(f"\r  [{i}/{len(urls)}] {symbol} {status or 'ERR':>4}  {msg[:40]:<40}", end='', flush=True)

    print('\n')

    # 统计
    ok_urls = [r for r in results if r[1] == 200]
    failed_urls = [r for r in results if r[1] != 200]

    print(f"📊 统计：")
    print(f"   总数：{len(results)}")
    print(f"   ✅ 成功（200）：{len(ok_urls)}")
    print(f"   ❌ 失败：{len(failed_urls)}")
    print()

    if failed_urls:
        print("❌ 失败 URL 详情：")
        for url, status, msg in sorted(failed_urls):
            print(f"   [{status or 'ERR'}] {url}")
            print(f"          → {msg}")
        print()
        print("⚠️  请检查：")
        print("   · 仓库是否已设置为 public")
        print("   · 文件名是否含特殊字符（中文需 URL 编码）")
        print("   · 是否已推送到指定分支")
        sys.exit(1)
    else:
        print("🎉 所有 URL 可正常访问！可以放心用 import_urls 批量入库 ima 知识库。")
        sys.exit(0)


if __name__ == '__main__':
    main()
