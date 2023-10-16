"""Build the sales report card and open it in the default image viewer."""

from report_image import build_report_image, load_sales_data

if __name__ == "__main__":
    build_report_image(load_sales_data()).show()
