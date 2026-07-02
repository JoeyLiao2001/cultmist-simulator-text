import sys
from pathlib import Path

# Add src/ to path so tests can import cleaner.*
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def read_fixture(name: str) -> str:
    """读取测试 fixture 文件的原始文本。"""
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")
