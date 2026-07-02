#!/usr/bin/env python3
"""Cultist Simulator 文本清洗工具 — CLI 入口。

Usage:
    python run_clean.py                          # 使用默认路径
    python run_clean.py --data-dir ./data --output-dir ./output
"""

import argparse
import sys
from pathlib import Path

from cleaner.pipeline import run_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="清洗 Cultist Simulator 文本数据为结构化 JSONL 数据集"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).parent,
        help="包含 14 个类别子目录的根目录（默认：项目根目录）"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent / "cleaned",
        help="输出目录（默认：./cleaned）"
    )
    args = parser.parse_args()

    if not args.data_dir.exists():
        print(f"错误：数据目录不存在：{args.data_dir}")
        sys.exit(1)

    print(f"数据目录: {args.data_dir}")
    print(f"输出目录: {args.output_dir}")
    print("正在清洗...")

    report = run_pipeline(args.data_dir, args.output_dir)

    print(f"\n=== 清洗报告 ===")
    print(f"  扫描文件: {report.total_files}")
    print(f"  提取成功: {report.extracted}")
    print(f"  解析成功: {report.parsed}")
    print(f"  清洗成功: {report.cleaned}")
    print(f"  校验通过: {report.validated}")
    print(f"  导出条数: {report.exported}")
    print(f"  错误数量: {report.errors}")

    if report.error_details:
        print(f"\n错误详情:")
        for err in report.error_details[:20]:  # 最多显示 20 条
            print(f"  - {err}")
        if len(report.error_details) > 20:
            print(f"  ... 及其他 {len(report.error_details) - 20} 条")

    print(f"\n输出文件:")
    for f in sorted(args.output_dir.glob("*")):
        print(f"  {f.name}")

    return 0 if report.errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
