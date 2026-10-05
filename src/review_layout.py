#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""排版 Review：把 A4 页面 HTML 渲染成图，交给 OpenRouter 免费视觉模型识图，
返回 [P0]/[P1]/[P2] 排版修正建议。

用法：
  python src/review_layout.py output/<oc>/index.html
  python src/review_layout.py output/<oc>/index.html --screenshot shot.png
  python src/review_layout.py output/<oc>/index.html --no-api   # 只渲染截图，不调用模型

环境变量：
  OPENROUTER_API_KEY        调用模型时必填；也可写在根目录 .env（OPENROUTER_API_KEY=...）
  OPENROUTER_REVIEW_MODEL   可选，默认 nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free

退出码：0 = 无 [P0]；1 = 发现 [P0]（可用 --no-gate 关闭）；2 = 用法/环境错误。

安全约束：本脚本是唯一允许使用该 Key 的地方。处理文字或代码时严禁调用、
读取或转发此 Key。
"""

import argparse
import base64
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

DEFAULT_MODEL = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

REVIEW_PROMPT = """你是密教模拟器 OC 展示页的排版评审员。检查图中的 A4 页面，规则以项目 prompts/page-design.md 为准。逐项核对：
1. 页面固定 A4（210×297mm）：不能出现滚动条、内容不能溢出页底或被裁切
2. 页边距 14mm，四周一致
3. hero 区：肖像 36×36mm，与角色名/引文/性相图标不重叠、不错位
4. 小传：4 段叙事，居中，max-width 150mm，不得出现星座中具体物品名
5. 物品区：tier2 占 50% 宽、sprite 20×20mm；tier3 占 33% 宽、sprite 15×15mm；缩略图与文字块对齐，文字无裁切、无重叠
6. 每件物品的性相图标集完整（类别性相 + 原则性相），透明度约 0.5
7. 颜色只用令牌：纸色 #ece4d5、暖墨 #2c2418、冷墨 #3c4048、灰墨 #5a4e3e、标签灰 #908070、淡灰 #6b5e4e；背景菱形肌理不喧宾夺主
8. 字体层级：角色名 15pt/400、引文 9pt 斜体、小传 8pt、物品名 8pt/600、物品描述 7pt、类型标签 5.5pt uppercase
9. 整体观感：克制、留白充足，无元素互相挤压

输出格式（每项一行，必须带具体位置描述，不要泛泛而谈）：
[P0] 必须修复：<位置> <问题>
[P1] 建议修复：<位置> <问题>
[P2] 可选项：<位置> <问题>
[PASS] <位置> <通过项>

若全部通过，只输出 [PASS] 行。禁止输出清单以外的内容。"""


def find_browser():
    for p in BROWSERS:
        if os.path.isfile(p):
            return p
    return None


def render_html(html_path, out_png, scale=2):
    browser = find_browser()
    if browser is None:
        raise SystemExit("未找到 Edge/Chrome，请用 --screenshot 提供已渲染的截图")
    url = pathlib.Path(html_path).resolve().as_uri()
    user_data_dir = tempfile.mkdtemp(prefix="cs-review-")
    cmd = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--disable-software-rasterizer",
        "--no-sandbox",
        "--disable-gpu-sandbox",
        "--no-first-run",
        "--disable-extensions",
        "--disable-background-networking",
        "--hide-scrollbars",
        "--force-device-scale-factor=" + str(scale),
        "--window-size=794,1123",
        "--virtual-time-budget=5000",
        "--user-data-dir=" + user_data_dir,
        "--screenshot=" + str(out_png),
        url,
    ]
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    try:
        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=90,
            creationflags=flags,
        )
    finally:
        shutil.rmtree(user_data_dir, ignore_errors=True)
    if not os.path.isfile(out_png) or os.path.getsize(out_png) == 0:
        raise SystemExit("渲染失败：未生成截图。请检查 HTML 或改用 --screenshot 提供已有截图")


def data_uri(png_path):
    b64 = base64.b64encode(pathlib.Path(png_path).read_bytes()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def load_api_key():
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        return key
    env_file = pathlib.Path(__file__).resolve().parent.parent / ".env"
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("OPENROUTER_API_KEY="):
                value = line.split("=", 1)[1].strip()
                return value.strip('"').strip("'")
    return None


def review(image_uri, model):
    if not model.endswith(":free"):
        raise SystemExit(
            f"仅允许 OpenRouter 免费模型（模型 ID 必须以 :free 结尾），当前模型：{model}。\n"
            "请用环境变量 OPENROUTER_REVIEW_MODEL 指定免费模型，例如 "
            "qwen/qwen2.5-vl-32b-instruct:free"
        )
    key = load_api_key()
    if not key:
        raise SystemExit(
            "缺少 OPENROUTER_API_KEY。请设置环境变量，或在根目录 .env 中写入：\n"
            "  OPENROUTER_API_KEY=sk-or-..."
        )
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": REVIEW_PROMPT},
                    {"type": "image_url", "image_url": {"url": image_uri}},
                ],
            }
        ],
        "max_tokens": 1200,
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=100) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        raise SystemExit(f"OpenRouter HTTP {e.code}: {body[:500]}")
    except urllib.error.URLError as e:
        raise SystemExit(f"网络错误：{e.reason}")
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise SystemExit(f"响应异常：{json.dumps(data, ensure_ascii=False)[:500]}")


def main():
    ap = argparse.ArgumentParser(
        description="渲染 HTML 并用 OpenRouter 免费视觉模型检查排版"
    )
    ap.add_argument("html", help="页面 HTML 路径")
    ap.add_argument("--screenshot", help="使用已有截图，跳过渲染")
    ap.add_argument("--screenshot-out", help="截图保存路径（默认与 HTML 同名 .review.png）")
    ap.add_argument("--scale", type=float, default=2.0, help="截图倍率，默认 2.0；免费模型慢/超时可降到 1.5")
    ap.add_argument(
        "--model",
        default=os.environ.get("OPENROUTER_REVIEW_MODEL", DEFAULT_MODEL),
        help=f"OpenRouter 免费模型，必须以 :free 结尾（默认 {DEFAULT_MODEL}）",
    )
    ap.add_argument("--no-api", action="store_true", help="只渲染截图，不调用模型")
    ap.add_argument("--no-gate", action="store_true", help="发现 [P0] 时不返回退出码 1")
    args = ap.parse_args()

    html = pathlib.Path(args.html)
    if not html.is_file():
        raise SystemExit(f"HTML 不存在：{html}")

    png = pathlib.Path(args.screenshot) if args.screenshot else None
    if png is None:
        png = pathlib.Path(args.screenshot_out) if args.screenshot_out else html.with_name(html.stem + ".review.png")
        print(f"[render] {html} -> {png}", flush=True)
        render_html(str(html), str(png), scale=args.scale)
    elif not png.is_file():
        raise SystemExit(f"截图不存在：{png}")

    if args.no_api:
        print(f"[ok] 截图已保存：{png}", flush=True)
        return

    print(f"[review] model={args.model}", flush=True)
    content = review(data_uri(png), args.model)
    print(content, flush=True)
    has_p0 = any(line.startswith("[P0]") for line in content.splitlines())
    if has_p0 and not args.no_gate:
        sys.exit(1)


if __name__ == "__main__":
    main()
