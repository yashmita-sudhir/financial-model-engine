# Financial Model Engine

A Natural Language to Linked 3-Statement Financial Model Engine.

The long-term goal of this project is to let a user describe business
assumptions in plain English and receive a fully linked Excel financial
model — Income Statement, Balance Sheet, and Cash Flow Statement — generated
from those assumptions.

This repository is currently at **Milestone 0: project foundation**. No
financial modeling logic exists yet.

## Architecture philosophy

The system is designed around a strict separation of concerns so that the
parts of the pipeline that touch money are deterministic and auditable,
while the parts that touch natural language are not trusted with
calculations:

1. **The LLM never calculates authoritative financial outputs.** Natural
   language is only ever translated into structured assumptions. All
   arithmetic happens in deterministic Python code that a human can read,
   test, and audit independently of any model output.
2. **Financial calculations are deterministic Python**, not LLM-generated
   formulas or LLM-computed numbers.
3. **Excel generation is separated from financial logic.** The engine that
   computes a model's numbers has no knowledge of spreadsheets, and the
   Excel writer has no knowledge of accounting rules — it only renders
   values and formulas it's given.
4. **Financial objects use stable, internal IDs**, not Excel cell
   references, so the underlying model is independent of any particular
   spreadsheet layout.
5. **Monetary and accounting calculations use Python's `Decimal`** where
   appropriate, to avoid floating-point error in financial output.
6. **The accounting engine enforces double-entry accounting.** A model
   that doesn't balance is treated as a bug, not a display issue.
7. **The system is test-driven and auditable** at every layer — from
   parsing assumptions, to computing statements, to generating the final
   workbook.

## Milestone roadmap

- **Milestone 0 — Project foundation** *(this milestone)*: repository
  structure, dependency setup, test configuration. No modeling logic.
- **Milestone 1 — Core domain models**: Pydantic models representing
  financial assumptions and statement line items, identified by stable IDs.
- **Milestone 2 — Deterministic calculation engine**: pure Python logic
  that computes statement values from assumptions.
- **Milestone 3 — Double-entry accounting enforcement**: dependency and
  balance validation, likely using NetworkX for the underlying graph.
- **Milestone 4 — Excel generation layer**: rendering a computed model to
  a linked `.xlsx` workbook using openpyxl, kept fully separate from the
  calculation engine.
- **Milestone 5 — Natural language interface**: LLM-assisted parsing of
  user descriptions into structured assumptions (never into numbers).
- **Milestone 6 — API layer**: a FastAPI service exposing the engine.
- **Milestone 7 — Frontend / UX**: a user-facing interface.

Milestones are implemented one at a time; later milestones are not started
until the current one is explicitly approved.

## Project structure

```
financial-model-engine/
├── src/
│   └── financial_model_engine/   # the package
└── tests/                        # pytest tests
```

## Getting started

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```
