from dataclasses import dataclass, field
from pathlib import Path

from cleaner.extract import extract_all
from cleaner.parse import parse_record
from cleaner.clean import clean_record
from cleaner.validate import validate_record, deduplicate
from cleaner.export import (
    export_jsonl, export_lite, export_parallel, export_stats, export_vocabulary,
)


@dataclass
class PipelineReport:
    """Pipeline 执行报告。"""
    data_dir: str = ""
    output_dir: str = ""
    total_files: int = 0
    extracted: int = 0
    parsed: int = 0
    cleaned: int = 0
    validated: int = 0
    exported: int = 0
    errors: int = 0
    error_details: list[str] = field(default_factory=list)


def run_pipeline(data_dir: Path, output_dir: Path) -> PipelineReport:
    """执行完整的 ETL pipeline。"""
    error_details: list[str] = []

    # 阶段 1: Extract
    raw_records = extract_all(data_dir)
    total_files = len(raw_records)

    # 阶段 2: Parse
    parsed_records = []
    for raw in raw_records:
        try:
            parsed_records.append(parse_record(raw))
        except Exception as e:
            error_details.append(f"Parse error [{raw.element_id}]: {e}")

    # 阶段 3: Clean
    cleaned_records = []
    for p in parsed_records:
        try:
            cleaned_records.append(clean_record(p))
        except Exception as e:
            error_details.append(f"Clean error [{p.element_id}]: {e}")

    # 阶段 4: Validate
    valid_records = []
    for c in cleaned_records:
        errors = validate_record(c)
        if errors:
            error_details.extend(f"Validation [{c.id}]: {err}" for err in errors)
        else:
            valid_records.append(c)

    # 去重
    unique_records = deduplicate(valid_records)

    # 阶段 5: Export
    output_dir.mkdir(parents=True, exist_ok=True)
    exported_count = 0
    try:
        exported_count += export_jsonl(unique_records, output_dir / "cs_dataset.jsonl")
        exported_count += export_lite(unique_records, output_dir / "cs_dataset_lite.jsonl")
        exported_count += export_parallel(unique_records, output_dir / "cs_parallel_zh_en.jsonl")
        export_stats(unique_records, output_dir / "cs_stats.json")
        export_vocabulary(unique_records, output_dir / "cs_vocabulary.txt")
    except Exception as e:
        error_details.append(f"Export error: {e}")

    return PipelineReport(
        data_dir=str(data_dir),
        output_dir=str(output_dir),
        total_files=total_files,
        extracted=len(raw_records),
        parsed=len(parsed_records),
        cleaned=len(cleaned_records),
        validated=len(unique_records),
        exported=exported_count,
        errors=len(error_details),
        error_details=error_details,
    )
