# Contributing

Contributions should keep the lab reproducible without hardware and must use synthetic examples.

## Local Validation

```bash
python -m pip install -e ".[dev]"
python -m ruff check .
python -m pytest --cov --cov-report=term-missing -q
```

## Data Rules

Do not add real device identifiers, customer information, corporate endpoints, private APNs, credentials, internal paths or proprietary command sequences.

