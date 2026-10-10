#!/usr/bin/env python3
"""
gen_urls.py — 生成仓库所有 .md 文件的 raw.githubusercontent.com URL 列表

用途：把生成的 URL 喂给 ima 知识库的 import_urls 工具，批量自动入库。

用法：
    python scripts/gen_urls.py                      # 默认读取当前仓库
    python scripts/gen_urls.py --owner yizhen-career --repo dai-yizhen-resume --branch main
    python scripts/gen_urls.py --only resumes/      # 只生成简历类
    python scripts/gen_urls.py --output urls.txt    # 自定义输出文件

输出：
    scripts/url-list.txt（默认）—— 每行一个 raw URL，UTF-8 编码

依赖：
    Python 3.6+（标准库 only，无第三方依赖）
"""

import argparse
import os
import sys
from pathlib import Path
from urllib.parse import quote


def find_markdown_files(repo_root: Path, include_dirs: list = None) -> list:
    """递归查找所有 .md 文件（排除指定目录）"""
    exclude_dirs = {'.git', '.github', 'node_modules', '__pycache__', 'venv', '.venv'}
    exclude_files = {'README_template.md', 'gitignore_template.txt'}  # 模板文件不入库

    md_files = []
    for root, dirs, files in os.walk(repo_root):
        # 跳过排除目录
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        # 如果指定了包含目录，只保留这些
        if include_dirs:
            rel_root = Path(root).relative_to(repo_root)
            if not any(str(rel_root).startswith(d) for d in include_dirs):
                continue

        for file in files:
            if file.endswith('.md') and file not in exclude_files:
                md_files.append(Path(root) / file)

    return sorted(md_files)


def build_raw_url(owner: str, repo: str, branch: str, file_path: Path) -> str:
    """构造 raw.githubusercontent.com URL"""
    # UTF-8 编码路径（中文文件名必须）
    encoded_path = quote(str(file_path).replace('\\', '/'), safe='/')
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{encoded_path}"


def chunk_list(lst: list, chunk_size: int = 10) -> list:
    """将列表分块，每块最多 chunk_size 个（ima import_urls 单次最多 10 个）"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def main():
    parser = argparse.ArgumentParser(
        description="生成仓库所有 .md 文件的 raw GitHub URL 列表（用于 ima 批量入库）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        '--owner', default=os.environ.get('GITHUB_OWNER', 'yizhen-career'),
        help='GitHub 用户名或组织名（默认读取环境变量 GITHUB_OWNER）',
    )
    parser.add_argument(
        '--repo', default='dai-yizhen-resume',
        help='仓库名（默认 dai-yizhen-resume）',
    )
    parser.add_argument(
        '--branch', default='main',
        help='分支名（默认 main）',
    )
    parser.add_argument(
        '--only', nargs='+', default=None,
        help='只包含指定目录，如 --only resumes reports',
    )
    parser.add_argument(
        '--output', default='scripts/url-list.txt',
        help='输出文件路径（默认 scripts/url-list.txt）',
    )
    parser.add_argument(
        '--no-ima-chunks', action='store_true',
        help='不按 ima 10 个一批分块（默认会按 10 个分块输出）',
    )

    args = parser.parse_args()

    # 仓库根目录（脚本所在位置的上一级）
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent

    # 查找所有 .md 文件
    md_files = find_markdown_files(repo_root, include_dirs=args.only)

    if not md_files:
        print(f"❌ 未找到任何 .md 文件（仓库根目录：{repo_root}）", file=sys.stderr)
        sys.exit(1)

    # 生成 URL 列表
    urls = [build_raw_url(args.owner, args.repo, args.branch, f) for f in md_files]

    # 写出
    output_path = repo_root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# URL 列表 — 自动生成于 {Path(__file__).name}\n")
        f.write(f"# 仓库：{args.owner}/{args.repo}@{args.branch}\n")
        f.write(f"# 文件总数：{len(urls)}\n")
        f.write(f"# ima import_urls 单次最多 10 个 → 分 {len(chunk_list(urls, 10))} 批\n\n")

        if args.no_ima_chunks:
            for url in urls:
                f.write(url + '\n')
        else:
            for chunk_idx, chunk in enumerate(chunk_list(urls, 10), 1):
                f.write(f"# ─── 批次 {chunk_idx}/{len(chunk_list(urls, 10))}（共 {len(chunk)} 个）───\n")
                for url in chunk:
                    f.write(url + '\n')
                f.write('\n')

    # 输出统计
    print(f"✅ 已生成 {len(urls)} 个 URL → {output_path}")
    print(f"   分 {len(chunk_list(urls, 10))} 批（每批最多 10 个，符合 ima import_urls 限制）")
    if args.only:
        print(f"   仅包含目录：{', '.join(args.only)}")
    print()
    print("📋 接下来：")
    print(f"   1. 检查 URL 列表：cat {output_path}")
    print(f"   2. 验证可访问：python scripts/verify_urls.py")
    print(f"   3. 喂给 ima：分批调用 mcp__ima-mcp__import_urls")


if __name__ == '__main__':
    main()
