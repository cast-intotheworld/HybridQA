"""Custom type aliases for the HybridQA serialization pipeline."""

# Identifier types
TableID = str
QuestionID = str
WikiURL = str

# Data structure types
CellValue = str
CellLinks = list[str]
HeaderCell = tuple[CellValue, CellLinks]
DataCell = tuple[CellValue, CellLinks]
TableRow = list[DataCell]

# Passage types
PassageMap = dict[WikiURL, str]

# Answer node: (text, (row_idx, col_idx), wiki_url, source_type)
AnswerNodeTuple = tuple[str, tuple[int, int], str | None, str]
