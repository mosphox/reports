import pytest
from reports.main import Record, Group, Review


@pytest.fixture
def dummy_records():
    return [
        Record(1, "Support", "x@y.com", "Hank", 5, 50),
        Record(2, "Support", "y@z.com", "Jane", 10, 75)
    ]


def test_review_initialization(dummy_records):
    group = Group("Support", dummy_records, addons=(("total", "hours"),))
    review = Review(groups=[group], fields=["name", "hours"])

    assert len(review.groups) == 1
    assert review.groups[0].name == "Support"
    assert review.fields == ["name", "hours"]


def test_review_with_empty_groups():
    review = Review(groups=[], fields=["name", "email"])
    assert review.groups == []
    assert review.fields == ["name", "email"]


def test_review_fields_order_matters(dummy_records):
    group = Group("Support", dummy_records, addons=(("total", "rate"),))
    review = Review(groups=[group], fields=["rate", "name"])

    assert review.fields[0] == "rate"
    assert review.fields[1] == "name"
