import json
import pytest
from reports.main import Record, PayoutReport, SaveToFile


@pytest.fixture
def payout_review():
    records = [
        Record(1, "QA", "qa1@mail.com", "Testy", 3, 100),
        Record(2, "QA", "qa2@mail.com", "Debuggy", 7, 150),
    ]
    return PayoutReport().create(records)


def test_save_as_json_creates_file(tmp_path, payout_review):
    file_path = tmp_path / "report"
    saver = SaveToFile(str(file_path), "json")
    saver.save(payout_review)

    full_path = tmp_path / "report.json"
    assert full_path.exists()

    with open(full_path, "r") as f:
        data = json.load(f)

    assert "QA" in data
    assert data["QA"]["records"][0]["name"] == "Testy"


def test_save_as_text_creates_file(tmp_path, payout_review):
    file_path = tmp_path / "summary"
    saver = SaveToFile(str(file_path), "text")
    saver.save(payout_review)

    full_path = tmp_path / "summary.txt"
    assert full_path.exists()

    with open(full_path, "r") as f:
        content = f.read()

    assert "Testy" in content
    assert "QA" in content


def test_invalid_format_raises_error(tmp_path):
    with pytest.raises(AttributeError, match="Forbidden magic"):
        SaveToFile(str(tmp_path / "output"), "xml")


def test_auto_extension_json(tmp_path, payout_review):
    file_path = tmp_path / "data.json"
    saver = SaveToFile(str(file_path), "json")
    saver.save(payout_review)

    assert file_path.exists()


def test_auto_extension_text(tmp_path, payout_review):
    file_path = tmp_path / "log.txt"
    saver = SaveToFile(str(file_path), "text")
    saver.save(payout_review)

    assert file_path.exists()
