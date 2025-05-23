import argparse
from collections import defaultdict
from dataclasses import dataclass
import json
from typing import List


@dataclass
class Record:
    """
    Represents a single employee's record with basic payroll-related fields.

    Attributes:
        employee_id (int): Just the employee's ID.
        department (str): The corporate tribe this soul belongs to.
        email (str): Contact address.
        name (str): The hero's real name.
        hours (int): Time served, in hours.
        rate (int): The price of one hour of their existence.
    """

    employee_id: int
    department: str
    email: str
    name: str
    hours: int
    rate: int

    def __post_init__(self):
        """
        Converts incoming string values to numbers where possible.
        """
        self.employee_id = self._to_number(self.employee_id)
        self.hours = self._to_number(self.hours, default=0)
        self.rate = self._to_number(self.rate, default=0)

    @staticmethod
    def _to_number(value, default=None):
        """
        Converts a value to int if it's a clean number, otherwise tries float.
        Falls back to a default if it's total nonsense.

        Args:
            value: Something vaguely number-ish.
            default: What to return if conversion fails (optional).

        Returns:
            int or float or the fallback thing.
        """
        try:
            number = float(value)
            return int(number) if number.is_integer() else number

        except ValueError:
            return default if default is not None else value


class Group:
    """
    Groups a bunch of Records by some shared identity — like a department.
    Can also inject magic fields via add_* methods, because static reports are boring.

    Attributes:
        name (str): The group label (e.g. department name).
        records (list): The poor souls in this group.
        addons (list): Tuple of method names and field names to auto-calculate cool stuff.
    """

    def __init__(self, name: str, records: List[Record], addons: tuple):
        """
        Initializes a Group and applies all the optional spicy add-ons.

        Raises:
            AttributeError: If an expected add_* method is missing.
        """
        self.name = name
        self.records = records
        self.addons = addons

        for method, field in addons:
            method_name = f"add_{method}"

            if hasattr(self, method_name):
                setattr(self, f"{method}_{field}", getattr(self, method_name)(field))

            else:
                raise AttributeError(f"Tried to call add_{method}, but that method ghosted us.")

    def __repr__(self) -> str:
        """Returns a quick preview of the group for nosy print statements."""
        return f"Group(name={self.name}, records={self.records})"

    def add_total(self, field: str) -> int:
        """
        Sums up a given field across all records. Great for hours, salaries, and broken dreams.

        Args:
            field (str): The attribute name to total.

        Returns:
            int or float: Total value of the field across records.
        """
        return sum(getattr(record, field) for record in self.records)


@dataclass
class Review:
    """
    A final glorious report.

    Attributes:
        groups (List[Group]): The organized data.
        fields (List[str]): What to show.
    """
    groups: List[Group]
    fields: List[str]


class Report:
    """
    The base report template. Extend this to make real reports.

    Attributes:
        groupby (str): Attribute to group records by. Like 'department' or 'blood type'.
        addons (tuple): Extra summary fields to add via add_* methods.
        include (list): Which fields to show in the final output. Defaults to all the usual suspects.

    Notes:
        To add a field into a report simply list it inside the include var like:
            include = [..., "field_name", ...]

        You need to create add_*field_name* method and pass records into it. There, you can set a new attr
        for a record with field name you've already listed above. Like:
            def add_custom_field(self, records):
                for record in records:
                    record.custom_field = "Hey! Sup?"

        Fields are added in the same order they appear in include list.
        Hence, if you need to add field_1 and then field_2 that includes field_1 in it's calculations
        - field_1 should appear before field_2 in the include list.

        All new reports should be mapped to a name into reports_map dict. (It's wandering somewhere at the bottom)
    """

    groupby = "employee_id"
    addons = ()

    include = ["department", "email", "name", "hours", "rate"]

    def add_fields(self, records: List[Record]) -> None:
        """
        Tries to add all the extra fields listed in `include`.
        If one’s missing, it panics (loudly) unless you provide an add_* method.

        Args:
            records (List[Record]): The data being sliced and diced.

        Raises:
            AttributeError: When you promise a field but forget to implement it.
        """
        for field in self.include:
            if field not in ["employee_id", "department", "email", "name", "hours", "rate"]:
                method_name = f"add_{field}"

                if hasattr(self, method_name):
                    getattr(self, method_name)(records)

                else:
                    raise AttributeError(f"'{field}' is missing and there's no '{method_name}' method to save the day.")

    def process(self, records: List[Record]) -> List[Group]:
        """
        Groups the records into bundles of joy — or just departments.

        Args:
            records (List[Record]): The raw material.

        Returns:
            List[Group]: Grouped records with optional add-ons.
        """
        grouped = defaultdict(list)
        [grouped[getattr(record, self.groupby)].append(record) for record in records]
        return [Group(key, value, self.addons) for key, value in grouped.items()]

    def create(self, records: List[Record]) -> Review:
        """
        Generates a shiny Review object from raw records.

        Args:
            records (List[Record]): Input data.

        Returns:
            Review: The final packaged report.
        """
        self.add_fields(records)
        groups = self.process(records)

        return Review(groups=groups, fields=self.include)


class PayoutReport(Report):
    """
    Groups by department and includes total hours + payout per unit.

    Attributes:
        groupby (str): Set to 'department', because HR said so.
        addons (tuple): Adds total hours and total payout per group.
        include (list): Fields to show, including computed 'payout'.
    """

    groupby = "department"
    addons = (("total", "hours"), ("total", "payout"), )

    include = ["name", "hours", "rate", "payout"]

    def add_payout(self, records: List[Record]) -> None:
        """
        Adds a payout field to each record (hours * rate).

        Args:
            records (List[Record]): The victims.
        """
        for record in records:
            record.payout = record.hours * record.rate


class Formatter:
    """
    Handles formatting of review data into various output formats.
    You define how it should look — this class doesn't save anything, just makes it pretty.

    Methods:
        console(review): Returns a nicely aligned text table of the data for console or txt.
        jsonfile(review): Returns a dictionary ready to be dumped into a JSON file.
    """

    def console(self, review: Review) -> str:
        """
        Formats the review into a human-readable table.

        Args:
            review (Review): The review data structure with groups and fields.

        Returns:
            str: A multi-line string that looks kinda like a spreadsheet.
        """
        rows = [[""] + [header.capitalize() for header in review.fields]]

        for group in review.groups:
            rows.append([group.name] + ["" for _ in range(len(review.fields))])

            for record in group.records:
                rows.append([""] + [getattr(record, field) for field in review.fields])

            addons = {review.fields.index(addon[1]): getattr(group, "_".join(addon)) for addon in group.addons}
            rows.append([""] + [addons.get(i, "") for i in range(len(review.fields))])

        widths = [max(len(str(cell)) for cell in column) for column in zip(*rows)]
        lines = ["   ".join(str(cell).ljust(width) for cell, width in zip(row, widths)) for row in rows]

        return "\n".join(lines)

    def jsonfile(self, review: Review) -> dict:
        """
        Formats the review into a JSON-ready dict.

        Args:
            review (Review): The review object to be serialized.

        Returns:
            dict: A nice little JSON-structured dictionary of your report data.
        """
        def format_record(record):
            return {field: getattr(record, field) for field in review.fields}

        formatted = {}
        for group in review.groups:
            formatted[group.name] = {"records": [format_record(record) for record in group.records]}
            addons = {"_".join(addon): getattr(group, "_".join(addon)) for addon in group.addons}
            formatted[group.name] = {**formatted[group.name], **addons}

        return formatted


class SaveToFile:
    """
    Saves a formatted report to a file — assuming you’ve told it what format you want.
    Requires a formatting method (via Formatter) to already exist.

    Usage:
        SaveToFile("output", "json").save(review)

    Attributes:
        filepath (str): Where the file should go.
        fileformat (str): What magical format to save as (e.g., 'json', 'text').
    """

    def __init__(self, filepath: str, fileformat: str):
        """
        Initializes the saver and binds the appropriate save method.
        Raises an error if you're trying to save in a format that doesn't exist.

        Args:
            filepath (str): Output file path.
            fileformat (str): Desired format ('json', 'text', etc.).

        Raises:
            AttributeError: If no save method exists for the given format.
        """
        self.filepath = filepath
        method_name = f"save_as_{fileformat}"

        if hasattr(self, method_name):
            self.save = getattr(self, method_name)
        else:
            raise AttributeError(f"Saving as '{fileformat}'? Forbidden magic. That format is not in the spellbook.")

    def respond(self) -> None:
        print(f"Report was saved to '{self.filepath}'. You're welcome.")

    def save_as_json(self, review: Review) -> None:
        """
        Saves the formatted review data as a JSON file.

        Args:
            data (Review): The review to save.
        """
        self.filepath += ".json" if not self.filepath.endswith(".json") else ""
        formatted = Formatter().jsonfile(review)

        with open(self.filepath, "w") as file:
            json.dump(formatted, file)

        self.respond()

    def save_as_text(self, review: Review) -> None:
        """
        Saves the formatted review as a plain text file — aligned and readable.

        Args:
            data (Review): The review to save.
        """
        self.filepath += ".txt" if not self.filepath.endswith(".txt") else ""
        formatted = Formatter().console(review)

        with open(self.filepath, "w") as file:
            file.write(formatted)

        self.respond()


def parse_args():
    """
    Parses command-line arguments for the almighty report generator.

    Returns:
        argparse.Namespace: All the glorious arguments you’ve passed in, neatly wrapped.
    """
    parser = argparse.ArgumentParser(
        description="Summon a report from the depths of chaotic CSV files and make sense of payroll data. "
                    "Supports multiple file inputs, report types, and fancy output options."
    )

    parser.add_argument(
        "files",
        metavar="FILES",
        nargs="+",
        help="One or more CSV files with employee metrics (like hours worked, rates, ...)."
    )

    parser.add_argument(
        "-r", "--report",
        required=True,
        help="Type of report to generate. (e.g. payout)"
    )

    parser.add_argument(
        "-s", "--silent",
        action="store_true",
        help="Suppress console output. Because maybe you're allergic to terminals, or you're just saving to a file."
    )

    parser.add_argument(
        "-o", "--output",
        help="Where to save the result. Leave blank to scream the report into the void (a.k.a. your console)."
    )

    parser.add_argument(
        "-f", "--format",
        default="json",
        help="Output format: 'json', 'text', or any other formats you like (just don't forget to add them)"
    )

    return parser.parse_args()


columns = ["id", "department", "email", "name", "hours_worked", "hourly_rate", "rate", "salary"]
reports_map = {
    "payout": PayoutReport,
    # add new reports here, they'll be callable from console under -r/--report flag
}


def load_records(filepath: str) -> List[Record]:
    """
    Loads employee records from a CSV file.

    Assumes the file has a header row with columns in any order.
    Automatically maps them to expected Record fields by position.
    If a column is missing or the structure is messed up, it'll complain loudly.

    Args:
        filepath (str): Path to the CSV file.

    Returns:
        List[Record]: List of Record instances loaded from the file.

    Raises:
        Exception: If something's wrong with the file (missing columns, bad format, etc.).
    """

    try:
        with open(filepath, "r") as file:
            lines = [line.strip().split(",") for line in file]

        order = [min(columns.index(column), 5) for column in lines[0]]
        return [Record(*(data[order.index(i)] for i in range(len(order)))) for data in lines[1:]]

    except Exception as error:
        print(f"Failed to load file: {filepath}")
        print("Probably not a valid CSV or the columns are out of whack.")
        print(f"Error: {error}")
        raise


def main():
    args = parse_args()

    records = [record for file in args.files for record in load_records(file)]
    report = reports_map.get(args.report)

    if not report:
        exit(f"Unknown report type '{args.report}'. Try one of: {', '.join(reports_map.keys())}. Or don't.")

    review = report().create(records)

    if not args.silent:
        print(Formatter().console(review))

    if args.output:
        SaveToFile(args.output, args.format).save(review)

    if args.silent and not args.output:
        print("Warning: You used --silent without specifying --output. "
              "So... you're generating a report and sending it straight into the void. Hope that was intentional.")


if __name__ == '__main__':
    main()
