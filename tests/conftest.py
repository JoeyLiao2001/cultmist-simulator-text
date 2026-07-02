from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def read_fixture(name: str) -> str:
    """读取测试 fixture 文件的原始文本。"""
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")
