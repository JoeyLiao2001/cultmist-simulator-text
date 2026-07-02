import pytest
from cleaner.models import ParsedRecord, CleanedRecord, I18nEntry
from cleaner.clean import (
    clean_aspects, clean_description, clean_i18n, clean_record
)


class TestCleanAspects:
    def test_normal(self):
        raw = ["[[刃]]", "[[诱发绝望]]", "[[影响]]"]
        result = clean_aspects(raw)
        assert result == ["刃", "诱发绝望", "影响"]

    def test_with_empty_brackets(self):
        raw = ["[[刃]]", "[[]]", "[[影响]]"]
        result = clean_aspects(raw)
        assert result == ["刃", "影响"]

    def test_empty_list(self):
        assert clean_aspects([]) == []


class TestCleanDescription:
    def test_normal(self):
        desc, has_inst, has_tmpl = clean_description("一段纯粹的叙事文本。")
        assert desc == "一段纯粹的叙事文本。"
        assert has_inst is False
        assert has_tmpl is False

    def test_with_game_instruction(self):
        desc, has_inst, has_tmpl = clean_description(
            "战前，我被邀请去亚历山大港。[一旦你离开，卡牌将消失。]"
        )
        assert "战前，我被邀请去亚历山大港。" in desc
        assert "[一旦你离开" not in desc
        assert has_inst is True
        assert has_tmpl is False

    def test_with_multiple_instructions(self):
        desc, has_inst, has_tmpl = clean_description(
            "文本开头。[指令一]中间文本。[指令二]"
        )
        assert "指令一" not in desc
        assert "指令二" not in desc
        assert "文本开头。" in desc
        assert "中间文本。" in desc
        assert has_inst is True

    def test_with_template_var(self):
        desc, has_inst, has_tmpl = clean_description(
            "斯人抚育我们，造就我们；斯人在流放中等待，必将于我们带来拂晓之时再起。"
        )
        # 描述本身不含 #VAR#，但 title 可能含，这里测 desc
        assert has_inst is False
        # has_template_var 由调用方根据 name + desc 一起判断

    def test_with_template_var_in_text(self):
        desc, has_inst, has_tmpl = clean_description(
            "我们的塑形者#PREVIOUSCHARACTERNAME#在等待。"
        )
        assert has_tmpl is True

    def test_empty_desc(self):
        desc, has_inst, has_tmpl = clean_description("")
        assert desc == ""
        assert has_inst is False
        assert has_tmpl is False


class TestCleanI18n:
    def test_normal(self):
        raw = {
            "en": {"label": "Dread", "desc": "I've seen too much. [game tip]"},
            "ja": {"label": "恐怖", "desc": "テスト。"},
        }
        result = clean_i18n(raw)
        assert result["en"].name == "Dread"
        assert "[game tip]" not in result["en"].desc
        assert result["ja"].name == "恐怖"

    def test_empty(self):
        assert clean_i18n({}) == {}


class TestCleanRecord:
    def test_full_clean(self):
        parsed = ParsedRecord(
            element_id="dread",
            category="influences",
            name="恐惧",
            desc_raw="我已经见得太多了。[游戏提示]",
            aspects_raw=["[[刃]]", "[[]]", "[[影响]]"],
            i18n_raw={
                "en": {"label": "Dread", "desc": "I've seen too much."}
            }
        )
        result = clean_record(parsed)
        assert result.id == "dread"
        assert result.name == "恐惧"
        assert "我已经见得太多了" in result.desc
        assert "[游戏提示]" not in result.desc
        assert result.aspects == ["刃", "影响"]
        assert result.meta.has_game_instruction is True
        assert result.meta.desc_length > 0

    def test_template_var_in_name(self):
        parsed = ParsedRecord(
            element_id="test",
            category="ascension",
            name="我们的塑形者#PREVIOUSCHARACTERNAME#",
            desc_raw="斯人抚育我们。",
            aspects_raw=[],
            i18n_raw={}
        )
        result = clean_record(parsed)
        assert result.meta.has_template_var is True
        assert "#PREVIOUSCHARACTERNAME#" in result.name

    def test_empty_desc_record(self):
        parsed = ParsedRecord(
            element_id="empty",
            category="spirits",
            name="空条",
            desc_raw="",
            aspects_raw=[],
            i18n_raw={}
        )
        result = clean_record(parsed)
        assert result.desc == ""
        assert result.meta.desc_length == 0
