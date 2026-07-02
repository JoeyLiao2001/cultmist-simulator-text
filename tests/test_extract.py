import pytest
from pathlib import Path
from cleaner.extract import split_frontmatter_body, extract_file, extract_all
from cleaner.models import RawRecord
from tests.conftest import FIXTURES_DIR


class TestSplitFrontmatterBody:
    def test_normal_file(self):
        text = (FIXTURES_DIR / "sample_dread.md").read_text("utf-8")
        fm, body = split_frontmatter_body(text)
        assert fm["element_id"] == "dread"
        assert fm["category"] == "influences"
        assert "# 恐惧" in body
        # body 不应包含 frontmatter 区域的内容（但可能仍含 Markdown 分割线 ---）
        assert "element_id: \"dread\"" not in body

    def test_no_frontmatter(self):
        text = "# Just a heading\n> some text"
        fm, body = split_frontmatter_body(text)
        assert fm == {}
        assert body == text


class TestExtractFile:
    def test_extract_dread(self):
        filepath = FIXTURES_DIR / "sample_dread.md"
        record = extract_file(filepath)
        assert record is not None
        assert record.element_id == "dread"
        assert record.category == "influences"
        assert "恐惧" in record.body
        assert "多语言对照" in record.body

    def test_extract_minimal(self):
        filepath = FIXTURES_DIR / "sample_minimal.md"
        record = extract_file(filepath)
        assert record is not None
        assert record.element_id == "simple.element"
        assert "简单物品" in record.body

    def test_extract_nonexistent_file(self):
        record = extract_file(Path("/nonexistent/file.md"))
        assert record is None


class TestExtractAll:
    def test_extract_all_from_fixtures(self, tmp_path):
        # 复制 fixtures 到临时目录模拟真实结构
        import shutil
        fixtures_dir = tmp_path / "influences"
        fixtures_dir.mkdir()
        for f in FIXTURES_DIR.glob("*.md"):
            shutil.copy(f, fixtures_dir / f.name)

        records = extract_all(tmp_path)
        assert len(records) >= 5
        ids = {r.element_id for r in records}
        assert "dread" in ids
        assert "simple.element" in ids

    def test_extract_all_empty_dir(self, tmp_path):
        records = extract_all(tmp_path)
        assert records == []
