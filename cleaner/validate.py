from cleaner.models import CleanedRecord


def validate_record(record: CleanedRecord) -> list[str]:
    """校验单条记录，返回错误列表（空 = 合规）。"""
    errors = []
    if not record.id:
        errors.append(f"missing id")
    if not record.name:
        errors.append(f"[{record.id}] missing name")
    if not record.category:
        errors.append(f"[{record.id}] missing category")
    return errors


def deduplicate(records: list[CleanedRecord]) -> list[CleanedRecord]:
    """按 id 去重，保留首次出现。"""
    seen: set[str] = set()
    result = []
    for r in records:
        if r.id not in seen:
            seen.add(r.id)
            result.append(r)
    return result
