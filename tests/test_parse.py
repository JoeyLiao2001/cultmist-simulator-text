import pytest
from pathlib import Path
from cleaner.models import RawRecord
from cleaner.parse import (
    parse_title, parse_description, parse_aspects,
    parse_i18n_table, parse_record
)
from tests.conftest import FIXTURES_DIR


def _raw_from_fixture(name: str) -> RawRecord:
    text = (FIXTURES_DIR / name).read_text("utf-8")
    # 手动构造 RawRecord 以便测试（绕过 extract）
    body_start = text.find("\n---\n", text.find("---\n") + 4)
    body = text[body_start + 5:] if body_start != -1 else text
    return RawRecord(
        element_id="test",
        category="test",
        source_file="test.json",
        body=body
    )


class TestParseTitle:
    def test_parse_title(self):
        body = "# 恐惧\n> `dread`\n> desc"
        assert parse_title(body) == "恐惧"

    def test_parse_title_with_template_var(self):
        body = "# 我们的塑形者#PREVIOUSCHARACTERNAME#\n> desc"
        assert parse_title(body) == "我们的塑形者#PREVIOUSCHARACTERNAME#"

    def test_parse_title_no_heading(self):
        body = "no heading here"
        assert parse_title(body) == ""


class TestParseDescription:
    def test_parse_normal_desc(self):
        body = "# 恐惧\n> `dread`\n\n> 我已经见得太多了。\n\n**Aspects:**"
        assert parse_description(body) == "我已经见得太多了。"

    def test_parse_none_desc(self):
        body = "# Test\n> `id`\n\n> None\n\n**Requirements:**"
        assert parse_description(body) == ""

    def test_parse_empty_desc_line(self):
        body = "# Test\n> `id`\n\n> \n\n**Aspects:**"
        assert parse_description(body) == ""

    def test_parse_game_instruction_desc(self):
        body = "# 亚历山大港\n> `city.alexandria`\n\n> 战前，我被邀请。[指令内容]\n\n**Aspects:**"
        result = parse_description(body)
        assert "战前，我被邀请。" in result
        assert "[指令内容]" in result  # parse 阶段保留原始文本


class TestParseAspects:
    def test_parse_aspects(self):
        body = "**Aspects:** [[刃]], [[诱发绝望]], [[影响]], [[健康欠佳]], [[回忆]]"
        aspects = parse_aspects(body)
        assert aspects == ["[[刃]]", "[[诱发绝望]]", "[[影响]]", "[[健康欠佳]]", "[[回忆]]"]

    def test_parse_aspects_with_empty(self):
        body = "**Aspects:** [[刃]], [[]], [[影响]]"
        aspects = parse_aspects(body)
        assert aspects == ["[[刃]]", "[[]]", "[[影响]]"]

    def test_parse_no_aspects(self):
        body = "**Slots:** 忆起"
        aspects = parse_aspects(body)
        assert aspects == []


class TestParseI18nTable:
    def test_parse_i18n_table(self):
        raw = _raw_from_fixture("sample_dread.md")
        i18n = parse_i18n_table(raw.body)
        assert "zh" in i18n
        assert i18n["zh"]["label"] == "恐惧"
        assert "我已经见得太多了" in i18n["zh"]["desc"]
        assert "en" in i18n
        assert i18n["en"]["label"] == "Dread"
        assert "ja" in i18n
        assert "ru" in i18n
        assert "de" in i18n

    def test_parse_no_i18n_table(self):
        raw = _raw_from_fixture("sample_minimal.md")
        i18n = parse_i18n_table(raw.body)
        assert i18n == {}


class TestParseRecord:
    def test_parse_dread(self):
        raw = _raw_from_fixture("sample_dread.md")
        parsed = parse_record(raw)
        assert parsed.name == "恐惧"
        assert "我已经见得太多了" in parsed.desc_raw
        assert len(parsed.aspects_raw) == 5
        assert "en" in parsed.i18n_raw

    def test_parse_empty_desc(self):
        raw = _raw_from_fixture("sample_empty_desc.md")
        parsed = parse_record(raw)
        assert parsed.desc_raw == ""

    def test_parse_template_var(self):
        raw = _raw_from_fixture("sample_template_var.md")
        parsed = parse_record(raw)
        assert "#PREVIOUSCHARACTERNAME#" in parsed.name
