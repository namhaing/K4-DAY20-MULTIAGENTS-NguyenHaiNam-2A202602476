#!/usr/bin/env python3
"""Thử thách mở rộng 6e - đo nhiễu bằng cách lặp lại các lần chạy trên tác vụ đánh giá.

Đọc nhiều thư mục kết quả (mỗi thư mục là một lần lặp, cùng cấu trúc `<dir>/<condition>/<task>/run.json`)
và in bảng Markdown: với mỗi điều kiện và tác vụ, điểm từng lần lặp, trung bình, khoảng dao động (max - min),
token trung bình; sau đó là các hàng tổng hợp theo điều kiện (tách check kỹ thuật và check quy ước `rule_`).

    python extras/noise_summary.py results results-rep1 results-rep2 --role eval > report/noise.md

Chỉ đọc `run.json`, không gọi mô hình, không sửa gì.
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean

ORDER = ["baseline", "subagents", "skills-auto"]


def load(dirs: list[str], role: str) -> dict:
    """{(condition, task): [run, ...]} theo thứ tự của `dirs`; bỏ qua lần chạy có `error`."""
    runs = defaultdict(list)
    for d in dirs:
        for f in sorted(Path(d).glob("*/*/run.json")):
            r = json.loads(f.read_text(encoding="utf-8"))
            if r.get("role") == role and r.get("condition") in ORDER and not r.get("error"):
                r["_dir"] = d
                runs[(r["condition"], r["task"])].append(r)
    return runs


def split(run: dict) -> tuple[int, int, int, int]:
    """(kỹ thuật đạt, kỹ thuật tổng, quy ước đạt, quy ước tổng)."""
    tech = [c for c in run["checks"] if not c["name"].startswith("rule_")]
    rule = [c for c in run["checks"] if c["name"].startswith("rule_")]
    return (sum(c["passed"] for c in tech), len(tech), sum(c["passed"] for c in rule), len(rule))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("dirs", nargs="+", help="thư mục kết quả, mỗi thư mục là một lần lặp")
    ap.add_argument("--role", default="eval", choices=["learn", "eval"])
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")   # bảng có tiếng Việt; console Windows mặc định cp1252
    runs = load(args.dirs, args.role)
    tasks = sorted({t for _, t in runs})

    print(f"Lặp lại: {', '.join(args.dirs)} (vai trò `{args.role}`)\n")
    print("| Điều kiện | Tác vụ | Điểm từng lần | Trung bình | Dao động (max-min) | Token TB |")
    print("|---|---|---|---|---|---|")
    for cond in ORDER:
        for task in tasks:
            rs = runs.get((cond, task), [])
            if not rs:
                continue
            scores = [r["score"] for r in rs]
            print(f"| {cond} | {task} | {', '.join(f'{s:.2f}' for s in scores)} | {mean(scores):.2f} "
                  f"| {max(scores) - min(scores):.2f} | {mean(r['tokens']['total'] for r in rs):,.0f} |")

    print("\n| Điều kiện | Số lần chạy | Điểm TB | Điểm TB thấp nhất / cao nhất theo lần lặp | Kỹ thuật đạt | Quy ước đạt | Token TB | Điểm / 100k token |")
    print("|---|---|---|---|---|---|---|---|")
    for cond in ORDER:
        rs = [r for (c, _), lst in runs.items() if c == cond for r in lst]
        if not rs:
            continue
        per_rep = defaultdict(list)
        for r in rs:
            per_rep[r["_dir"]].append(r["score"])
        rep_means = [mean(v) for v in per_rep.values()]
        tp, tt, rp, rt = (sum(x) for x in zip(*(split(r) for r in rs)))
        tok = mean(r["tokens"]["total"] for r in rs)
        print(f"| {cond} | {len(rs)} | {mean(r['score'] for r in rs):.3f} | {min(rep_means):.3f} / {max(rep_means):.3f} "
              f"| {tp}/{tt} | {rp}/{rt} | {tok:,.0f} | {mean(r['score'] for r in rs) / tok * 1e5:.2f} |")


if __name__ == "__main__":
    main()
