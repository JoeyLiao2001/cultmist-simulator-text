import json
import jsonlines
from pathlib import Path
from cleaner.models import CleanedRecord, RecordMeta, I18nEntry
from cleaner.export import (
    export_jsonl, export_lite, export_parallel, export_stats, export_vocabulary
)


def _sample_records():
    return [
        CleanedRecord(
            id="dread", name="恐惧",
            desc="我已经见得太多了。",
            category="influences",
            aspects=["刃", "影响"],
            i18n={
                "en": I18nEntry(name="Dread", desc="I've seen too much.")
            },
            meta=RecordMeta(desc_length=11, has_game_instruction=False, has_template_var=False)
        ),
        CleanedRecord(
            id="empty", name="空条",
            desc="",
            category="spirits",
            aspects=[],
            i18n={},
            meta=RecordMeta(desc_length=0, has_game_instruction=False, has_template_var=False)
        ),
    ]


def test_export_jsonl(tmp_path):
    output = tmp_path / "test.jsonl"
    count = export_jsonl(_sample_records(), output)
    assert count == 2
    assert output.exists()
    with jsonlines.open(output) as reader:
        records = list(reader)
    assert len(records) == 2
    assert records[0]["id"] == "dread"
    assert records[0]["meta"]["desc_length"] == 11


def test_export_lite(tmp_path):
    output = tmp_path / "lite.jsonl"
    count = export_lite(_sample_records(), output)
    assert count == 1  # 只有 desc_length > 10 的条目
    with jsonlines.open(output) as reader:
        records = list(reader)
    assert len(records) == 1
    # Lite 不应包含 i18n 或 meta
    assert "i18n" not in records[0]
    assert "meta" not in records[0]


def test_export_parallel(tmp_path):
    output = tmp_path / "parallel.jsonl"
    count = export_parallel(_sample_records(), output)
    assert count == 1  # 只有有英文翻译的
    with jsonlines.open(output) as reader:
        records = list(reader)
    assert records[0]["zh"] == "我已经见得太多了。"
    assert records[0]["en"] == "I've seen too much."


def test_export_stats(tmp_path):
    output = tmp_path / "stats.json"
    export_stats(_sample_records(), output)
    assert output.exists()
    stats = json.loads(output.read_text("utf-8"))
    assert stats["total"] == 2
    assert "by_category" in stats
    assert stats["by_category"]["influences"] == 1
    assert stats["by_category"]["spirits"] == 1
    assert stats["empty_desc"] == 1
    assert "desc_length" in stats


def test_export_vocabulary(tmp_path):
    output = tmp_path / "vocab.txt"
    export_vocabulary(_sample_records(), output)
    assert output.exists()
    content = output.read_text("utf-8")
    # 应该包含 aspects
    assert "刃" in content
    assert "影响" in content
