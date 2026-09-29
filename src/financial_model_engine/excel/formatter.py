from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from financial_model_engine.domain import Unit

TITLE_FONT = Font(bold=True, size=14)
HEADER_FONT = Font(bold=True)

ASSUMPTION_INPUT_FILL = PatternFill(
    start_color="FFF9DB", end_color="FFF9DB", fill_type="solid"
)

NUMBER_FORMATS: dict[Unit, str] = {
    Unit.CURRENCY: "$#,##0.00",
    Unit.PERCENTAGE: "0.0%",
    Unit.COUNT: "#,##0",
    Unit.DAYS: "#,##0",
    Unit.RATIO: "0.00",
}

GENERIC_VALUE_FORMAT = "#,##0.00"


def set_column_widths(worksheet: Worksheet, widths: dict[str, int]) -> None:
    for column_letter, width in widths.items():
        worksheet.column_dimensions[column_letter].width = width
