from dataclasses import dataclass
from enum import StrEnum


class GraphNodeType(StrEnum):
    ASSUMPTION = "assumption"
    LINE_ITEM = "line_item"


@dataclass(frozen=True)
class GraphNode:
    id: str
    type: GraphNodeType
