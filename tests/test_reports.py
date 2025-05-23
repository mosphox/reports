import pytest
from reports.main import Record, PayoutReport, Report


@pytest.fixture
def sample_records():
    return [
        Record(1, "HR", "hr1@mail.com", "Anna", 10, 50),
        Record(2, "HR", "hr2@mail.com", "Ben", 5, 40),
        Record(3, "Finance", "fin@mail.com", "Carl", 20, 100),
    ]


def test_payout_report_creates_review(sample_records):
    report = PayoutReport()
    review = report.create(sample_records)

    assert len(review.groups) == 2
    assert review.fields == ["name", "hours", "rate", "payout"]

    hr_group = next(g for g in review.groups if g.name == "HR")
    assert hr_group.total_hours == 15
    assert hr_group.total_payout == 10 * 50 + 5 * 40


def test_payout_field_is_added(sample_records):
    report = PayoutReport()
    report.add_fields(sample_records)

    assert hasattr(sample_records[0], "payout")
    assert sample_records[0].payout == 10 * 50


def test_missing_add_method_raises(sample_records):
    class BadReport(Report):
        include = ["name", "mystery_field"]

    with pytest.raises(AttributeError, match="add_mystery_field"):
        BadReport().add_fields(sample_records)


def test_empty_data_gives_empty_groups():
    report = PayoutReport()
    review = report.create([])
    assert review.groups == []
    assert review.fields == ["name", "hours", "rate", "payout"]
