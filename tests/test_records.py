from reports.main import Record


def test_creating():
    record = Record("1", "IT", "alice@example.com", "Alice", "40", "50")

    assert record.employee_id == 1
    assert record.department == "IT"
    assert record.email == "alice@example.com"
    assert record.name == "Alice"
    assert record.hours == 40
    assert record.rate == 50


def test_employee_id_converts_to_int_if_possible_else_str():
    record_int = Record("1", "IT", "alice@example.com", "Alice", "40", "50")
    record_str = Record("some_id", "IT", "alice@example.com", "Alice", "40", "50")

    assert record_int.employee_id == 1
    assert record_str.employee_id == "some_id"


def test_hours_and_rate_convert_to_int_if_possible_else_defaults_to_zero():
    record_valid_hours = Record("1", "IT", "alice@example.com", "Alice", "40", "50")
    record_invalid_hours = Record("1", "IT", "alice@example.com", "Alice", "forty", "50")
    record_valid_rate = Record("1", "IT", "alice@example.com", "Alice", "40", "50")
    record_invalid_rate = Record("1", "IT", "alice@example.com", "Alice", "40", "fifty")

    assert record_valid_hours.hours == 40
    assert record_invalid_hours.hours == 0
    assert record_valid_rate.rate == 50
    assert record_invalid_rate.rate == 0


def test_hours_and_rate_convert_to_float_if_possible_else_defaults_to_zero():
    record_valid_hours = Record("1", "IT", "alice@example.com", "Alice", "40.4", "50")
    record_invalid_hours = Record("1", "IT", "alice@example.com", "Alice", "forty", "50")
    record_valid_rate = Record("1", "IT", "alice@example.com", "Alice", "40", "50.5")
    record_invalid_rate = Record("1", "IT", "alice@example.com", "Alice", "40", "fifty")

    assert record_valid_hours.hours == 40.4
    assert record_invalid_hours.hours == 0
    assert record_valid_rate.rate == 50.5
    assert record_invalid_rate.rate == 0


def test_record_to_number_explicitly():
    assert Record._to_number("5") == 5
    assert Record._to_number("5.5") == 5.5
    assert Record._to_number("garbage", default=-1) == -1
    assert Record._to_number("garbage") == "garbage"
    assert Record._to_number("") == ""
    assert Record._to_number("", default=0) == 0
