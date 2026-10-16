"""Library fine and book renewal tracker for a campus library."""

import ast
import json
import operator
from datetime import datetime

FINE_PER_DAY = 2
EXTENDED_RENEWAL_DAYS = 14
ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
}

loans = {}
loan_dates = {}


def add_book_loan(student_id, book_id, dates=None):
    """Record that a student has borrowed a book."""
    if not student_id:
        print("Cannot record a loan without a student ID")
        return
    if dates is None:
        dates = loan_dates.setdefault(student_id, [])
    book_id = str(book_id)
    dates.append(str(datetime.now()))
    loans[student_id] = loans.get(student_id, []) + [book_id]
    print(f"{student_id} borrowed {book_id} "
          f"(loan dates on record: {len(dates)})")


def return_book(student_id, book_id):
    """Remove a book from a student's loans, if it is on record."""
    try:
        loans[student_id].remove(book_id)
        if not loans[student_id]:
            del loans[student_id]
    except (KeyError, ValueError):
        print(f"Cannot return {book_id}: no such loan for {student_id}")


def calculate_fine(days_overdue, rate=FINE_PER_DAY):
    """Return the fine for the given number of overdue days."""
    return max(days_overdue, 0) * rate


def renew_book(student_id, book_id, extra_days):
    """Renew a loan and return the fine rate that applies to it."""
    rate = FINE_PER_DAY
    if extra_days > EXTENDED_RENEWAL_DAYS:
        rate += 1
    print(f"Renewed {book_id} for {student_id} by {extra_days} days "
          f"(fine rate: {rate}/day)")
    return rate


def load_records(file="loans.json"):
    """Load loan records from a JSON file."""
    with open(file, "r", encoding="utf-8") as f:
        loans.clear()
        loans.update(json.load(f))


def save_records(file="loans.json"):
    """Save loan records to a JSON file."""
    with open(file, "w", encoding="utf-8") as f:
        json.dump(loans, f)


def _safe_eval(node, days):
    """Evaluate an arithmetic expression tree that may use 'days'."""
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body, days)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name) and node.id == "days":
        return days
    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPS:
        left = _safe_eval(node.left, days)
        right = _safe_eval(node.right, days)
        return ALLOWED_OPS[type(node.op)](left, right)
    raise ValueError("Unsupported expression in fine rule")


def fine_from_rule(rule, days):
    """Compute a fine from a simple rule such as 'days * 2 + 10'."""
    return _safe_eval(ast.parse(rule, mode="eval"), days)


def print_report():
    """Print every student's current loans."""
    print("Loan Report")
    for student, books in loans.items():
        print(student, "->", books)


def read_days(prompt):
    """Ask for a non-negative whole number of days (Enter means 0)."""
    answer = input(prompt).strip() or "0"
    try:
        return max(int(answer), 0)
    except ValueError:
        print(f"'{answer}' is not a number, using 0")
        return 0


def main():
    """Run a short demonstration of the library system."""
    add_book_loan("S101", "B-ALGO")
    add_book_loan("S102", "B-NETW")
    add_book_loan("", "B-DBMS")
    add_book_loan("S103", 4521)
    return_book("S999", "B-NONE")
    rate = renew_book("S101", "B-ALGO", 21)
    print("Fine for 5 days:", calculate_fine(5))
    print("Fine for 5 days on renewed loan:", calculate_fine(5, rate))
    print("Fine for -3 days:", calculate_fine(-3))
    print("Fine via rule:", fine_from_rule("days * 2 + 10", 4))
    days = read_days("Days overdue for S102 (press Enter for 0): ")
    print("S102 owes:", calculate_fine(days))
    save_records()
    load_records()
    print_report()


if __name__ == "__main__":
    main()
