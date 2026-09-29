class CellMapper:
    """Records where line items and assumptions were written in a workbook.

    Populated as a side effect of writing cells, so it can never drift from
    what the workbook actually contains.
    """

    def __init__(self) -> None:
        self._line_item_cells: dict[tuple[str, str, str], str] = {}
        self._assumption_cells: dict[str, tuple[str, str]] = {}

    def map_line_item(
        self, line_item_id: str, period_id: str, sheet_name: str, cell_ref: str
    ) -> None:
        self._line_item_cells[(line_item_id, period_id, sheet_name)] = cell_ref

    def get_line_item_cell(
        self, line_item_id: str, period_id: str, sheet_name: str
    ) -> str:
        return self._line_item_cells[(line_item_id, period_id, sheet_name)]

    def map_assumption(self, assumption_id: str, sheet_name: str, cell_ref: str) -> None:
        self._assumption_cells[assumption_id] = (sheet_name, cell_ref)

    def get_assumption_cell(self, assumption_id: str) -> tuple[str, str]:
        return self._assumption_cells[assumption_id]
