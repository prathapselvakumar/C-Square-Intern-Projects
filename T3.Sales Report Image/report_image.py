"""Draw the daily sales comparison card.

The card compares the current day ("C") with the previous day ("P") using the
figures in sales_data.json. Each metric gets an up or down arrow showing
whether the current day was higher than the previous one, and the figures for
both days are written onto a background template.
"""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "sales_data.json"
BACKGROUND_IMAGE = BASE_DIR / "template_background.jpg"
UP_ARROW_IMAGE = BASE_DIR / "up_arrow.jpg"
DOWN_ARROW_IMAGE = BASE_DIR / "down_arrow.jpg"
FONT_FILE = BASE_DIR / "impact.ttf"
OUTPUT_IMAGE = BASE_DIR / "report_output.png"

FONT_SIZE = 40
TEXT_COLOURS = {
    "C": (199, 21, 133),  # current day
    "P": (199, 21, 133),  # previous day
}
DEFAULT_TEXT_COLOUR = (0, 0, 0)

# (metric, arrow position, arrow size). Positions are pixel offsets on the template.
ARROW_LAYOUT = [
    ("InvoiceTotal", (240, 370), (30, 60)),
    ("InvoiceCount", (240, 470), (30, 60)),
    ("InvoiceAvg", (240, 570), (30, 60)),
    ("InvoiceCustomerCount", (240, 670), (30, 60)),
    ("InvoiceLineCount", (240, 770), (30, 60)),
    ("NetSale", (235, 1110), (40, 70)),
]

# (field, y position, x for current day, x for previous day).
TEXT_LAYOUT = [
    ("DocDt", 280, 275, 10),
    ("InvoiceTotal", 380, 275, 10),
    ("InvoiceCount", 480, 290, 50),
    ("InvoiceAvg", 580, 290, 50),
    ("InvoiceCustomerCount", 680, 290, 50),
    ("InvoiceLineCount", 780, 290, 50),
]
NET_SALE_Y = 1120
NET_SALE_X = (300, 40)  # current day, previous day


def load_sales_data(path=DATA_FILE):
    """Return the [current day, previous day] records from the JSON file."""
    with open(path, "r") as data_file:
        return json.load(data_file)


def format_lakhs(amount):
    """Convert rupees to lakhs with three decimals, e.g. 31289067 -> '312.891L'."""
    return "{:,.3f}L".format(float(amount) / 100000)


def build_report_image(sales_data):
    """Return the finished report card as a PIL image."""
    current_day, previous_day = sales_data[0], sales_data[1]

    report = Image.open(BACKGROUND_IMAGE).copy()
    up_arrow = Image.open(UP_ARROW_IMAGE)
    down_arrow = Image.open(DOWN_ARROW_IMAGE)
    draw = ImageDraw.Draw(report)
    font = ImageFont.truetype(str(FONT_FILE), FONT_SIZE)

    # Down arrow when the current day is below the previous day, otherwise up.
    for metric, position, size in ARROW_LAYOUT:
        went_down = float(current_day[metric]) < float(previous_day[metric])
        arrow = down_arrow if went_down else up_arrow
        report.paste(arrow.resize(size), position)

    # Write the figures for both days: current on the right, previous on the left.
    for day_index, day in enumerate((current_day, previous_day)):
        colour = TEXT_COLOURS.get(day["dayType"], DEFAULT_TEXT_COLOUR)
        for field, y, current_x, previous_x in TEXT_LAYOUT:
            x = current_x if day_index == 0 else previous_x
            draw.text((x, y), day[field], font=font, fill=colour)
        draw.text((NET_SALE_X[day_index], NET_SALE_Y), format_lakhs(day["NetSale"]), font=font, fill=colour)

    return report


def save_report_image(path=OUTPUT_IMAGE):
    """Build the report from sales_data.json, save it, and return the file path."""
    report = build_report_image(load_sales_data())
    report.save(path)
    return path
