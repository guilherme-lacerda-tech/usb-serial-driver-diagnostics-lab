# ADR 0001: Simulation-First Diagnostics

## Status

Accepted.

## Context

USB serial troubleshooting normally depends on physical adapters, Windows driver state and which process currently owns the COM port. A public portfolio project cannot rely on specific hardware and must not expose private device evidence.

## Decision

The project uses a simulation-first diagnostic engine. Live probing is supported, but all CI, examples and docs are built around synthetic scenarios.

## Consequences

- The project is demonstrable on any machine.
- Tests can cover failure modes that are hard to reproduce on demand.
- Hardware validation remains explicitly pending until real lab hardware is used.

