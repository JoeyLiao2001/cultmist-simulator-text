import pytest
from cleaner.models import CleanedRecord, RecordMeta
from cleaner.validate import validate_record, deduplicate


class TestValidateRecord:
    def test_valid_record(self):
        r = CleanedRecord(
            id="dread", name="恐惧", desc="文本。",
            category="influences", aspects=["刃"],
            i18n={}, meta=RecordMeta(desc_length=3)
        )
        errors = validate_record(r)
        assert errors == []

    def test_missing_id(self):
        r = CleanedRecord(
            id="", name="恐惧", desc="文本。",
            category="influences", aspects=[],
            i18n={}, meta=RecordMeta(desc_length=3)
        )
        errors = validate_record(r)
        assert len(errors) > 0
        assert any("id" in e.lower() for e in errors)

    def test_missing_name(self):
        r = CleanedRecord(
            id="test", name="", desc="文本。",
            category="influences", aspects=[],
            i18n={}, meta=RecordMeta(desc_length=3)
        )
        errors = validate_record(r)
        assert len(errors) > 0

    def test_missing_category(self):
        r = CleanedRecord(
            id="test", name="测试", desc="文本。",
            category="", aspects=[],
            i18n={}, meta=RecordMeta(desc_length=3)
        )
        errors = validate_record(r)
        assert len(errors) > 0


class TestDeduplicate:
    def test_no_duplicates(self):
        r1 = CleanedRecord(id="a", name="A", desc="", category="x",
                           aspects=[], i18n={}, meta=RecordMeta(desc_length=0))
        r2 = CleanedRecord(id="b", name="B", desc="", category="x",
                           aspects=[], i18n={}, meta=RecordMeta(desc_length=0))
        result = deduplicate([r1, r2])
        assert len(result) == 2

    def test_with_duplicates(self):
        r1 = CleanedRecord(id="a", name="A1", desc="", category="x",
                           aspects=[], i18n={}, meta=RecordMeta(desc_length=0))
        r2 = CleanedRecord(id="a", name="A2", desc="", category="y",
                           aspects=[], i18n={}, meta=RecordMeta(desc_length=0))
        result = deduplicate([r1, r2])
        assert len(result) == 1
        # 保留第一个
        assert result[0].name == "A1"
