# Harmonia Optimizer
## Evaluation.md
### Version 1.0

Author: 皿田 孝
Technical Advisor: ChatGPT

---

# 1. Purpose

This document defines the evaluation methodology used by Harmonia Optimizer.

The objective is to evaluate keyboard layouts objectively using reproducible quantitative metrics rather than subjective impressions.

All evaluation modules are independent and produce normalized scores.

---

# 2. Evaluation Philosophy

A keyboard layout should be evaluated from multiple independent viewpoints.

The evaluation system consists of four major categories.

```
Physical Ergonomics

↓

Typing Efficiency

↓

Language Adaptation

↓

Usability
```

Each category contains several independent metrics.

---

# 3. Overall Score

```
Overall Score

=

Σ (Metric × Weight)
```

Default range

```
0

～

100
```

Higher is better.

---

# 4. Evaluation Categories

```
Overall

├── Physical
├── Typing
├── Language
└── Usability
```

---

# 5. Physical Ergonomics

Measures physical effort.

Modules

```
Finger Load

Hand Balance

Travel Distance

Row Usage

Finger Strength

Lateral Stretch

Same Finger

Thumb Usage

Layer Cost
```

---

## 5.1 Finger Load

Purpose

Balance workload across fingers.

Ideal

```
Index

>

Middle

>

Ring

>

Pinky
```

Output

```
0～100
```

---

## 5.2 Hand Balance

Purpose

Balance left and right hand usage.

Ideal

```
50%

/

50%
```

Allowable range

```
45%

～

55%
```

Penalty increases outside this range.

---

## 5.3 Travel Distance

Measures total finger movement.

```
Home

↓

Minimal movement

↓

Higher score
```

Physical coordinates are used.

---

## 5.4 Row Usage

Evaluates row distribution.

Ideal

```
Home

>

Upper

>

Lower
```

Example

```
Home

65%

Upper

22%

Lower

13%
```

---

## 5.5 Finger Strength

Keys assigned according to finger strength.

Preferred order

```
Index

Middle

Ring

Pinky
```

High-frequency letters should avoid weak fingers.

---

## 5.6 Lateral Stretch

Measures sideways finger movement.

Penalty

```
Index

Inner

↓

Outer

↓

Large Stretch
```

Large lateral motion reduces score.

---

## 5.7 Same Finger Bigram

Consecutive use of identical finger.

Examples

```
ed

ki

ju
```

Penalty depends on

- distance
- row
- finger

Lower frequency is better.

---

## 5.8 Thumb Usage

Evaluates thumb utilization.

Includes

```
Space

Layer

Modifiers

Combos
```

Future support

Multiple thumb keys.

---

## 5.9 Layer Cost

Measures

Layer Hold

Layer Tap

Layer Switch

Penalty

```
Layer frequency

×

Activation cost
```

---

# 6. Typing Efficiency

Measures typing smoothness.

Modules

```
Alternation

Rolling

Trigram

Redirect

Finger Repeat
```

---

## 6.1 Hand Alternation

Alternating hands.

Ideal

```
L

R

L

R

L

R
```

Long one-hand sequences decrease score.

---

## 6.2 Rolling

Evaluates inward/outward rolls.

Preferred

```
Outer

↓

Inner
```

Example

```
S

D

F
```

Penalty

```
Reverse Roll
```

---

## 6.3 Redirect

Finger direction reversal.

Example

```
Index

↓

Middle

↓

Index
```

Large penalties for repeated reversals.

---

## 6.4 Finger Repeat

Repeated use of same finger.

Different from Same Finger Bigram.

Measures

Long repetition chains.

---

## 6.5 Trigram Smoothness

Evaluates

Three-character transitions.

Example

```
the

ing

tion

ent
```

---

# 7. Language Adaptation

Language-specific evaluation.

Modules

```
Japanese

English

Programming

Markdown

Terminal
```

---

## 7.1 Japanese

Corpus

Japanese frequency list.

Metrics

Kana conversion

Romanization

Roll

Alternation

Same finger

---

## 7.2 English

Corpus

Large English corpus.

Metrics

Letter frequency

Digraphs

Trigraphs

Word frequency

---

## 7.3 Programming

Corpus

Source code.

Languages

```
Python

TypeScript

Rust

C++

Go

Java
```

Metrics

Symbols

CamelCase

snake_case

Bracket usage

Operator usage

---

## 7.4 Markdown

Measures

```
#

*

-

`

[]

()

```

Useful for documentation writing.

---

## 7.5 Terminal

Measures

```
/

\

-

_

.

~

:

;
```

Useful for Linux and Windows terminal usage.

---

# 8. Shortcut Evaluation

Measures common shortcuts.

Examples

```
Ctrl+C

Ctrl+V

Ctrl+X

Ctrl+Z

Ctrl+A

Ctrl+S

Ctrl+F

Ctrl+P
```

Evaluates

Finger movement

Modifier position

Roll

Same finger

Home Row Mod compatibility

---

# 9. Gaming Evaluation (Future)

Measures

```
WASD

Modifier

Mouse

Thumb

Layer
```

Optional module.

---

# 10. Layer Evaluation

Measures

```
Layer access frequency

Layer switching cost

Layer hold duration

Thumb usage
```

Supports

Entropy

ZMK

QMK

---

# 11. Combo Evaluation

Measures

```
Combo size

Finger symmetry

Distance

Timing
```

Supports

```
Combo

Tap Dance

Auto Shift

Leader Key
```

---

# 12. Home Row Modifier Evaluation

Measures

```
False Hold

Typing latency

Shortcut compatibility

Home Row congestion
```

One of Harmonia's primary evaluation metrics.

---

# 13. Physical Keyboard Evaluation

Independent from logical layout.

Supports

```
Corne

Halcyon

Entropy

K:04 mini

Future keyboards
```

Metrics

Reachability

Thumb angle

Finger angle

Travel distance

---

# 14. Weight Profiles

Different users need different priorities.

Profiles

```
Japanese

English

Programming

Gaming

Balanced

Research
```

Example

Programming

```
Programming

40%

English

20%

Japanese

15%

Shortcut

15%

Ergonomics

10%
```

---

# 15. Evaluation Pipeline

```
Layout

↓

Corpus

↓

Tokenizer

↓

Bigram

↓

Trigram

↓

Evaluation Modules

↓

Weighted Score

↓

Final Report
```

---

# 16. Score Normalization

Every metric returns

```
0

～

100
```

Normalization

```
Raw Score

↓

Scaling

↓

Weight

↓

Overall Score
```

---

# 17. Benchmark Layouts

Reference layouts

```
QWERTY

Colemak

Colemak-DH

Graphite

Hands Down

Gallium

Canary

Harmonia
```

Every release compares against benchmark layouts.

---

# 18. Future Metrics

Future research

```
Heatmap

Typing Fatigue

EMG Analysis

Machine Learning

Adaptive Evaluation

Personalized Profiles
```

---

# 19. Validation

Evaluation correctness verified by

```
Unit Test

Corpus Test

Benchmark Comparison

Regression Test

Real Typing Data
```

---

# 20. Harmonia-Specific Evaluation

Additional metrics unique to Harmonia.

```
AIUEO placement

Home Row Modifier efficiency

Thumb utilization

Combo dependency

Layer dependency

Left-right vowel balance

Programming symbol efficiency

Japanese Romanization efficiency

Shortcut compatibility

Finger load budget
```

These metrics distinguish Harmonia from general keyboard layout optimizers.

---

# 21. Evaluation Priority

The optimizer applies metrics in the following order.

```
1. Hard Constraints
    ↓
2. Finger Load
    ↓
3. Same Finger
    ↓
4. Travel Distance
    ↓
5. Roll
    ↓
6. Alternation
    ↓
7. Language Score
    ↓
8. Programming Score
    ↓
9. Shortcut Score
    ↓
10. Overall Score
```

Hard constraints eliminate invalid layouts before scoring.

---

# 22. Design Principles

The evaluation engine shall satisfy the following:

- Every metric is independent.
- Every metric is configurable.
- Weights are externally defined.
- No hard-coded layout assumptions.
- Physical and logical evaluations remain separate.
- Results are deterministic and reproducible.

---

# End of Evaluation.md