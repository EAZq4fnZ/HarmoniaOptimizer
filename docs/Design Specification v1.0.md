# Harmonia Optimizer
## Design Specification v1.0

Author: 皿田 孝
Designer: ChatGPT
Language: Python 3.14+
License: MIT (Tentative)

---

# 1. Purpose

Harmonia Optimizer is a corpus-driven keyboard layout optimization system.

The project aims to evaluate and optimize keyboard layouts for:

- Japanese
- English
- Programming
- Shortcut usage
- Ergonomics

using reproducible quantitative metrics.

---

# 2. Goals

The optimizer shall:

- Compare arbitrary keyboard layouts
- Evaluate typing efficiency
- Analyze finger load
- Analyze hand balance
- Analyze roll patterns
- Analyze same-finger bigrams
- Optimize layouts automatically
- Produce reproducible reports

---

# 3. Design Philosophy

The project follows these principles.

## 3.1 Separation of Concerns

Logical Layout

↓

Physical Layout

↓

Evaluation

↓

Optimization

↓

Reporting

Each layer must remain independent.

---

## 3.2 Data Driven

Everything should be represented as data.

No keyboard layout is hard coded.

Layouts are stored as JSON.

Evaluation parameters are configurable.

---

## 3.3 Extensibility

The optimizer must support:

- Harmonia
- QWERTY
- Colemak
- Graphite
- Hands Down
- Onishi Layout
- Future layouts

without modifying evaluation code.

---

# 4. Architecture

Project

├── Models
├── Layout Loader
├── Corpus Loader
├── Evaluation Engine
├── Optimization Engine
├── Report Generator

---

# 5. Directory Structure

HarmoniaOptimizer/

main.py

README.md

requirements.txt

.gitignore

models/

layouts/

corpus/

evaluation/

optimizer/

report/

tests/

---

# 6. Models

## Position

Represents logical key position.

Fields

- layer
- hand
- finger
- row
- column

---

## PhysicalPosition

Represents physical coordinates.

Fields

- x
- y

Optional.

Used for distance calculations.

---

## Key

Represents one logical key.

Fields

- label
- logical_position
- physical_position
- category

---

## Layout

Represents one keyboard layout.

Fields

- name
- description
- language
- keys

Methods

- add_key()
- get_key()
- remove_key()

---

# 7. Layout Format

JSON

{
    "name": "...",

    "keys": [...]
}

No layout shall be hard coded.

---

# 8. Corpus

Supported corpora

Japanese

English

Programming

Markdown

Terminal

Each corpus has:

name

language

weight

token list

---

# 9. Evaluation Engine

Modules

Finger Load

Hand Balance

Alternation

Same Finger Bigram

Roll

Travel Distance

Programming Score

Shortcut Score

Language Score

Each module returns

0.0

～

100.0

---

# 10. Final Score

Overall score

=

Weighted Sum

Default

Japanese

40%

English

20%

Programming

20%

Shortcut

10%

Ergonomics

10%

Weights are configurable.

---

# 11. Optimization Engine

Algorithms

Random Search

Beam Search

Hill Climbing

Simulated Annealing

Genetic Algorithm

Multiple algorithms can coexist.

---

# 12. Reports

Markdown

CSV

JSON

HTML

Future

Interactive Dashboard

---

# 13. Testing

pytest

Unit Test

Integration Test

Regression Test

Coverage

>90%

---

# 14. Coding Standards

Python

PEP8

Type Hint Required

Dataclass Preferred

No Global Variables

Pure Functions Preferred

---

# 15. Performance Targets

26-key layout

Evaluation

<5 ms

Optimization

100,000 layouts/hour

Memory

<500 MB

---

# 16. Future Roadmap

v1

Evaluation

v2

Automatic Optimization

v3

GUI

v4

Interactive Editor

v5

Machine Learning Assisted Optimization

---

# 17. Current Development Status

Phase 1

☑ Environment

☑ Position

☑ Key

☑ Layout

□ JSON Loader

□ Corpus

□ Evaluation

□ Optimization

□ Report

---

End of Specification


