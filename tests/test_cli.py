import sys

import pytest

from reports.main import parse_args, load_records, main


# Sample CSV content
SAMPLE_CSV = """id,department,email,name,hours_worked,hourly_rate
1,Dev,dev@a.com,Alice,10,100
2,Dev,dev2@b.com,Bob,5,80
"""


def test_parse_args_with_all(monkeypatch):
    test_args = [
        "prog",
        "dummy.csv",
        "-r", "payout",
        "-f", "text",
        "-o", "result.txt",
        "-s"
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    args = parse_args()

    assert args.files == ["dummy.csv"]
    assert args.report == "payout"
    assert args.format == "text"
    assert args.output == "result.txt"
    assert args.silent is True


def test_parse_args_defaults(monkeypatch):
    test_args = [
        "prog",
        "some.csv",
        "-r", "payout"
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    args = parse_args()

    assert args.format == "json"
    assert args.output is None
    assert args.silent is False


def test_load_records_parses_csv(tmp_path):
    path = tmp_path / "test.csv"
    path.write_text(SAMPLE_CSV)

    records = load_records(str(path))
    assert len(records) == 2
    assert records[0].name == "Alice"
    assert records[1].hours == 5


def test_load_records_invalid_csv_throws(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("completely,invalid,csv\none,line,only")

    with pytest.raises(Exception):
        load_records(str(path))


def test_main_text_output(tmp_path, monkeypatch, capsys):
    csv_path = tmp_path / "data.csv"
    csv_path.write_text(SAMPLE_CSV)

    output_path = tmp_path / "out"
    test_args = [
        "prog",
        str(csv_path),
        "-r", "payout",
        "-f", "text",
        "-o", str(output_path),
    ]
    monkeypatch.setattr(sys, "argv", test_args)

    main()

    result_txt = output_path.with_suffix(".txt")
    assert result_txt.exists()
    content = result_txt.read_text()
    assert "Alice" in content
    assert "Bob" in content


def test_main_warns_about_silent_without_output(tmp_path, monkeypatch, capsys):
    csv_path = tmp_path / "data.csv"
    csv_path.write_text(SAMPLE_CSV)

    test_args = [
        "prog",
        str(csv_path),
        "-r", "payout",
        "-s"
    ]
    monkeypatch.setattr(sys, "argv", test_args)

    main()

    captured = capsys.readouterr()
    assert "Warning" in captured.out
    assert "void" in captured.out.lower()
