# attendance.py
"""Utilities for viewing or exporting attendance records."""
import csv
import argparse

from utils import init_db, get_attendance_records


def export_csv(path: str = "attendance.csv"):
    records = get_attendance_records()
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Date", "Time"])
        writer.writerows(records)
    print(f"Exported {len(records)} rows to {path}")


def main():
    init_db()

    parser = argparse.ArgumentParser(description="Attendance helper scripts")
    parser.add_argument("--export", "-e", help="Path to CSV file to write", default="attendance.csv")
    parser.add_argument("--show", "-s", action="store_true", help="Print attendance records to console")
    args = parser.parse_args()

    if args.show:
        for row in get_attendance_records():
            print(row)
    if args.export:
        export_csv(args.export)


if __name__ == "__main__":
    main()
