import pytest
from reports.main import Record, Group


@pytest.fixture
def sample_records():
    return [
        Record("1", "IT", "alice@example.com", "Alice", "40", "50"),
        Record("2", "IT", "bob@example.com", "Bob", "100", "40")
    ]


def test_creating(sample_records):
    group = Group("IT", sample_records, addons=())

    assert group.name == "IT"
    assert group.records == sample_records
    assert group.addons == ()


def test_repr(sample_records):
    group = Group("IT", sample_records, addons=())
    rep = repr(group)

    assert "Group(name=IT" in rep


def test_add_total_hours(sample_records):
    group = Group("IT", sample_records, addons=(("total", "hours"),))

    assert group.total_hours == 140


def test_add_total_rate(sample_records):
    group = Group("IT", sample_records, addons=(("total", "rate"),))

    assert group.total_rate == 90


def test_total_on_empty_field():
    records = [
        Record(1, "Ops", "x@y.com", "Void", 0, 0),
        Record(2, "Ops", "z@y.com", "Null", 0, 0),
    ]
    group = Group("Ops", records, addons=(("total", "hours"),))

    assert group.total_hours == 0


def test_missing_add_method_raises():
    records = [Record(1, "IT", "it@mail.com", "Ghost", 5, 50)]

    with pytest.raises(AttributeError, match="add_fake"):
        Group("IT", records, addons=(("fake", "hours"),))
