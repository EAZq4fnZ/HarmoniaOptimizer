# Harmonia Optimizer
## Architecture.md
### Version 1.0
Author: 皿田 孝
Technical Advisor: ChatGPT

---

# 1. Purpose

This document defines the software architecture of Harmonia Optimizer.

Unlike Specification.md, which describes **what the system should do**, this document defines **how the system is organized**.

The architecture emphasizes:

- Modularity
- Extensibility
- Testability
- Performance
- Separation of concerns

---

# 2. Overall Architecture

```
                 +----------------------+
                 |       main.py        |
                 +----------+-----------+
                            |
             +--------------+--------------+
             |                             |
     +-------v--------+          +---------v---------+
     | Configuration  |          |   Layout Loader   |
     +-------+--------+          +---------+---------+
             |                             |
             |                     +-------v-------+
             |                     | Layout Model  |
             |                     +-------+-------+
             |                             |
             |                     +-------v-------+
             |                     | Corpus Loader |
             |                     +-------+-------+
             |                             |
             +-----------------------------+
                                           |
                                   +-------v-------+
                                   | Evaluation    |
                                   +-------+-------+
                                           |
                                   +-------v-------+
                                   | Optimizer     |
                                   +-------+-------+
                                           |
                                   +-------v-------+
                                   | Report Engine |
                                   +---------------+
```

---

# 3. Package Structure

```
harmonia_optimizer/

│
├── main.py
│
├── models/
│
├── layouts/
│
├── corpus/
│
├── evaluation/
│
├── optimizer/
│
├── reports/
│
├── config/
│
├── utils/
│
└── tests/
```

Each package has exactly one responsibility.

---

# 4. Layer Architecture

```
Presentation

↓

Application

↓

Domain

↓

Infrastructure
```

---

## Presentation

Responsible for

- CLI
- GUI
- Reports

Never performs evaluation.

---

## Application

Coordinates

- loading
- evaluation
- optimization

Contains no business logic.

---

## Domain

Core of the project.

Contains

Layout

Key

Position

Corpus

Evaluation

Optimization

---

## Infrastructure

Responsible for

JSON

CSV

Filesystem

Configuration

Logging

---

# 5. Core Models

```
                Position
                    ▲
                    │
                 Key
                    ▲
                    │
                Layout
```

---

## Position

Represents one logical key location.

```
Layer

↓

Hand

↓

Finger

↓

Row

↓

Column
```

No character information exists here.

---

## Key

Represents one key.

```
Key

├── label

├── category

├── Position
```

Examples

```
"A"

"Esc"

"Enter"

"Shift"

";"
```

---

## Layout

Represents one complete layout.

```
Layout

├── metadata

├── keys

└── statistics
```

---

# 6. Evaluation Architecture

Evaluation is completely modular.

```
Evaluation Engine

│

├── Finger Load

├── Same Finger

├── Roll

├── Alternation

├── Stretch

├── Travel Distance

├── Programming

├── Shortcut

└── Layer Usage
```

Every evaluator implements the same interface.

```
evaluate(layout, corpus)

↓

Score
```

---

# 7. Optimizer Architecture

```
Optimizer

│

├── Random Search

├── Hill Climbing

├── Beam Search

├── Simulated Annealing

└── Genetic Algorithm
```

Each optimizer produces

```
Layout

↓

Score
```

The evaluation engine is shared.

---

# 8. Report Architecture

```
Evaluation Result

↓

Markdown

↓

CSV

↓

JSON

↓

HTML
```

Reports never evaluate layouts.

They only display results.

---

# 9. Layout Loader

```
JSON

↓

Validation

↓

Layout

↓

Evaluation
```

Supported formats

```
JSON

Future

YAML

TOML
```

---

# 10. Corpus Loader

```
TXT

CSV

↓

Tokenizer

↓

Frequency Table

↓

Corpus
```

Supports

Japanese

English

Programming

Markdown

Terminal

---

# 11. Configuration

```
config/

evaluation.json

weights.json

optimization.json

report.json
```

No constants should be embedded inside code.

---

# 12. Class Relationships

```
Layout

contains

↓

Key

contains

↓

Position
```

Evaluation never modifies them.

They are immutable.

---

# 13. Dependency Graph

```
main

↓

Application

↓

Evaluation

↓

Layout

↓

Key

↓

Position
```

Dependencies are one-directional.

Circular dependencies are forbidden.

---

# 14. UML Overview

```
+--------------------+
| Position           |
+--------------------+
| layer              |
| hand               |
| finger             |
| row                |
| column             |
+--------------------+

          ▲

+--------------------+
| Key                |
+--------------------+
| label              |
| category           |
| position           |
+--------------------+

          ▲

+--------------------+
| Layout             |
+--------------------+
| name               |
| description        |
| keys               |
+--------------------+

          ▲

+--------------------+
| EvaluationResult   |
+--------------------+
| score              |
| metrics            |
+--------------------+
```

---

# 15. Design Rules

Every class has one responsibility.

Immutable whenever possible.

No evaluation logic inside models.

No file I/O inside models.

No optimization logic inside reports.

---

# 16. Future Components

```
GUI

↓

Visualizer

↓

Heatmap

↓

Statistics Dashboard

↓

Layout Editor

↓

Corpus Editor
```

These modules must not modify the evaluation engine.

---

# 17. Performance Considerations

Use

```
dict
```

instead of

```
list
```

for key lookup.

Prefer

```
dataclass(slots=True)
```

to reduce memory usage.

Avoid object creation inside evaluation loops.

Cache repeated computations.

---

# 18. Error Handling

All modules raise custom exceptions.

Examples

```
LayoutError

CorpusError

EvaluationError

OptimizationError

ConfigurationError
```

---

# 19. Testing Strategy

Every package contains independent tests.

```
tests/

models/

evaluation/

optimizer/

reports/
```

Unit tests

↓

Integration tests

↓

Regression tests

---

# 20. Development Workflow

```
Design

↓

Implementation

↓

Unit Test

↓

Integration Test

↓

Benchmark

↓

Documentation

↓

Release
```

---

# 21. Long-Term Architecture

```
                 GUI
                  │
                  ▼
        Harmonia Optimizer API
                  │
      ┌───────────┼───────────┐
      ▼           ▼           ▼
 Evaluation   Optimizer   Reports
      │           │           │
      └───────────┼───────────┘
                  ▼
             Core Models
                  │
                  ▼
           Layout / Corpus
```

The **Core Models** layer is the foundation of the entire project. Every future feature—including a GUI, layout editor, web API, or machine-learning-based optimizer—must depend on the core models, but the core models themselves must remain independent of higher-level modules.

---

# End of Architecture.md