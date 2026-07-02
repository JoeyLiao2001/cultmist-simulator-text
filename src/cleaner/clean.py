import re
from cleaner.models import ParsedRecord, CleanedRecord, RecordMeta, I18nEntry


def clean_aspects(raw: list[str]) -> list[str]:
    """去掉 [[]] 包裹，过滤空内容。"""
    result = []
    for a in raw:
        inner = a.strip()
        if inner.startswith("[[") and inner.endswith("]]"):
            inner = inner[2:-2]
        if inner:  # 过滤空字符串（原 [[]]）
            result.append(inner)
    return result


def clean_description(desc: str) -> tuple[str, bool, bool]:
    """
    清洗描述文本。
    返回: (cleaned_text, has_game_instruction, has_template)
    """
    has_instruction = False

    # 移除 [游戏指令]
    cleaned, count = re.subn(r'\[[^\]]*\]', '', desc)
    if count > 0:
        has_instruction = True
        # 清理多余空格
        cleaned = re.sub(r'\s{2,}', ' ', cleaned)
        # 清理句号后缺少空格，以及多余标点
        cleaned = re.sub(r'。\s*。', '。', cleaned)
        cleaned = re.sub(r'，\s*，', '，', cleaned)
        cleaned = cleaned.strip()

    # 检测模板变量 #VAR#
    has_template = bool(re.search(r'#[A-Z_]+#', desc))

    return cleaned, has_instruction, has_template


def clean_i18n(raw: dict[str, dict]) -> dict[str, I18nEntry]:
    """清洗多语言数据。"""
    result = {}
    for lang_code, entry in raw.items():
        name = entry.get("label", "")
        desc = entry.get("desc", "")
        # 同样清洗 i18n 中的游戏指令
        desc_clean, _, _ = clean_description(desc)
        result[lang_code] = I18nEntry(name=name, desc=desc_clean)
    return result


def clean_record(parsed: ParsedRecord) -> CleanedRecord:
    """清洗单条 ParsedRecord 为 CleanedRecord。"""
    desc_clean, has_inst, has_tmpl_desc = clean_description(parsed.desc_raw)

    # 模板变量可能出现在 name 或 desc 中
    has_tmpl_name = bool(re.search(r'#[A-Z_]+#', parsed.name))
    has_template = has_tmpl_desc or has_tmpl_name

    return CleanedRecord(
        id=parsed.element_id,
        name=parsed.name,
        desc=desc_clean,
        category=parsed.category,
        aspects=clean_aspects(parsed.aspects_raw),
        i18n=clean_i18n(parsed.i18n_raw),
        meta=RecordMeta(
            desc_length=len(desc_clean),
            has_game_instruction=has_inst,
            has_template_var=has_template,
        ),
    )
