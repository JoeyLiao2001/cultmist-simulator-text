import json
from dataclasses import asdict
from cleaner.models import RawRecord, ParsedRecord, CleanedRecord, RecordMeta, I18nEntry


def test_raw_record_creation():
    r = RawRecord(
        element_id="dread",
        category="influences",
        source_file="abilities.json",
        body="# 恐惧\n> description text"
    )
    assert r.element_id == "dread"
    assert r.category == "influences"


def test_parsed_record_creation():
    r = ParsedRecord(
        element_id="dread",
        category="influences",
        name="恐惧",
        desc_raw="我已经见得太多了。",
        aspects_raw=["[[刃]]", "[[影响]]"],
        i18n_raw={"en": {"label": "Dread", "desc": "I've seen too much."}}
    )
    assert r.name == "恐惧"
    assert len(r.aspects_raw) == 2


def test_cleaned_record_creation():
    r = CleanedRecord(
        id="dread",
        name="恐惧",
        desc="我已经见得太多了。",
        category="influences",
        aspects=["刃", "影响"],
        i18n={
            "en": I18nEntry(name="Dread", desc="I've seen too much.")
        },
        meta=RecordMeta(
            desc_length=11,
            has_game_instruction=False,
            has_template_var=False
        )
    )
    assert r.id == "dread"
    assert r.meta.desc_length == 11
    assert r.meta.has_game_instruction is False


def test_cleaned_record_serializable():
    """CleanedRecord 应该可以序列化为 JSON。"""
    r = CleanedRecord(
        id="dread",
        name="恐惧",
        desc="测试文本。",
        category="influences",
        aspects=["刃"],
        i18n={
            "en": I18nEntry(name="Dread", desc="Test text.")
        },
        meta=RecordMeta(desc_length=5, has_game_instruction=False, has_template_var=False)
    )
    d = asdict(r)
    json_str = json.dumps(d, ensure_ascii=False)
    assert "恐惧" in json_str
    parsed = json.loads(json_str)
    assert parsed["id"] == "dread"
    assert parsed["meta"]["desc_length"] == 5


def test_record_meta_defaults():
    m = RecordMeta(desc_length=0)
    assert m.has_game_instruction is False
    assert m.has_template_var is False
