import json
import shutil
from pathlib import Path

from cleaner.pipeline import run_pipeline
from tests.conftest import FIXTURES_DIR


def test_pipeline_end_to_end(tmp_path):
    # 建立模拟数据目录
    data_dir = tmp_path / "data" / "influences"
    data_dir.mkdir(parents=True)
    for f in FIXTURES_DIR.glob("*.md"):
        shutil.copy(f, data_dir / f.name)

    output_dir = tmp_path / "output"
    report = run_pipeline(data_dir, output_dir)

    assert report.total_files >= 5
    assert report.parsed == report.total_files
    assert report.cleaned == report.total_files
    assert report.errors == 0

    # 检查输出文件
    assert (output_dir / "cs_dataset.jsonl").exists()
    assert (output_dir / "cs_dataset_lite.jsonl").exists()
    assert (output_dir / "cs_parallel_zh_en.jsonl").exists()
    assert (output_dir / "cs_stats.json").exists()
    assert (output_dir / "cs_vocabulary.txt").exists()

    # 验证 stats 内容
    stats = json.loads((output_dir / "cs_stats.json").read_text("utf-8"))
    assert stats["total"] >= 5
    assert "influences" in stats["by_category"]


def test_pipeline_empty_dir(tmp_path):
    data_dir = tmp_path / "empty_data"
    data_dir.mkdir()
    output_dir = tmp_path / "output"
    report = run_pipeline(data_dir, output_dir)
    assert report.total_files == 0
    assert report.parsed == 0
