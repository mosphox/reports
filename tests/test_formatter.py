import pytest
from reports.main import Record, PayoutReport, Formatter


@pytest.fixture
def payout_review():
    records = [
        Record(1, "Dev", "dev1@work.com", "Alice", 5, 10),
        Record(2, "Dev", "dev2@work.com", "Bob", 10, 20),
    ]
    report = PayoutReport()
    return report.create(records)


def test_console_output(payout_review):
    output = Formatter().console(payout_review)

    assert isinstance(output, str)
    assert "Name" in output
    assert "Alice" in output
    assert "Bob" in output
    assert "Dev" in output

    assert output.count("\n") == 4


def test_json_output_structure(payout_review):
    output = Formatter().jsonfile(payout_review)

    assert isinstance(output, dict)
    assert "Dev" in output

    dev_group = output["Dev"]
    assert "records" in dev_group
    assert isinstance(dev_group["records"], list)
    assert len(dev_group["records"]) == 2
    assert dev_group["records"][0]["name"] == "Alice"

    assert "total_hours" in dev_group
    assert "total_payout" in dev_group
    assert dev_group["total_hours"] == 15
    assert dev_group["total_payout"] == 5 * 10 + 10 * 20


def test_json_output_respects_field_order(payout_review):
    json_data = Formatter().jsonfile(payout_review)
    record = json_data["Dev"]["records"][0]
    fields = list(record.keys())

    assert fields == ["name", "hours", "rate", "payout"]
