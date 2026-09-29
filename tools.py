import re

import pandas as pd


EXCEL_FILE = "excel_data.xlsx"


def find_employee_name(text):
    """Find a unique employee name mentioned in a question."""

    df = pd.read_excel(EXCEL_FILE)
    names = df["Name"].dropna().astype(str).unique()
    matches = [
        name for name in names
        if re.search(rf"\b{re.escape(name)}\b", text, re.IGNORECASE)
    ]

    return matches[0] if len(matches) == 1 else None


def get_employee(name):
    """
    Find an employee by name.
    """

    df = pd.read_excel(EXCEL_FILE)

    employee = df[
        df["Name"].str.lower() == name.lower()
    ]

    if employee.empty:
        return f"Employee '{name}' was not found."

    row = employee.iloc[0]

    return {
        "name": row["Name"],
        "department": row["Department"],
        "joining_date": pd.to_datetime(row["Joining Date"]).strftime("%Y-%m-%d"),
        "salary": int(row["Salary"])
    }


def get_department_employees(department):
    """
    Find all employees in a department.
    """

    df = pd.read_excel(EXCEL_FILE)

    employees = df[
        df["Department"].str.lower() == department.lower()
    ]

    if employees.empty:
        return f"No employees found in {department} department."

    result = []

    for _, row in employees.iterrows():
        result.append({
            "name": row["Name"],
            "department": row["Department"],
            "joining_date": pd.to_datetime(row["Joining Date"]).strftime("%Y-%m-%d"),
            "salary": int(row["Salary"])
        })

    return result