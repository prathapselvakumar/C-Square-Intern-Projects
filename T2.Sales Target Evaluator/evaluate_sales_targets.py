"""Label each salesperson as a winner or loser against their sales target.

Reads data.xlsx (columns: code, name, dob, sales, target), adds a `result`
column, and writes the table to winners.xlsx. The input file is not changed.
"""

import pandas as pd

INPUT_FILE = "data.xlsx"
OUTPUT_FILE = "winners.xlsx"


def evaluate_result(row):
    """Return "winner" if sales met the target, otherwise "loser"."""
    return "loser" if row["sales"] < row["target"] else "winner"


def main():
    sales_data = pd.read_excel(INPUT_FILE)

    # Earlier runs saved the pandas index as extra "Unnamed: 0" columns; drop them.
    sales_data = sales_data.loc[:, ~sales_data.columns.str.startswith("Unnamed")]

    sales_data["result"] = sales_data.apply(evaluate_result, axis=1)
    print(sales_data)
    sales_data.to_excel(OUTPUT_FILE, index=False)


if __name__ == "__main__":
    main()
