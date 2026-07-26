# Harmonia Optimizer
## Algorithm.md
### Version 1.0

Author: 皿田 孝
Technical Advisor: ChatGPT

---

# 1. Purpose

This document defines the optimization algorithms used by Harmonia Optimizer.

The optimizer searches for keyboard layouts that maximize the evaluation score while satisfying predefined ergonomic constraints.

Unlike the Evaluation Engine, which only scores layouts, the Optimization Engine generates new candidate layouts.

---

# 2. Optimization Philosophy

The optimization engine follows four principles.

- Constraint First
- Data Driven
- Reproducible
- Algorithm Independent

All optimization algorithms share the same evaluation engine.

```
Layout

↓

Mutation

↓

Evaluation

↓

Selection

↓

Next Layout
```

---

# 3. Optimization Pipeline

```
Initial Layout

↓

Constraint Check

↓

Mutation

↓

Evaluation

↓

Selection

↓

Termination Check

↓

Best Layout
```

---

# 4. Hard Constraints

Invalid layouts are rejected before evaluation.

Examples

- Duplicate keys
- Missing alphabet
- Invalid layer assignment
- Invalid thumb assignment
- Forbidden shortcut conflicts
- Required symbol missing

Hard constraints return

```
Rejected
```

without evaluation.

---

# 5. Search Space

The optimizer explores

```
Alphabet

26!

×

Layer Assignment

×

Modifier Assignment

×

Combo Assignment
```

The search space is astronomically large.

Therefore exhaustive search is impossible.

---

# 6. Optimization Algorithms

The optimizer supports multiple search algorithms.

```
Random Search

↓

Hill Climbing

↓

Beam Search

↓

Simulated Annealing

↓

Genetic Algorithm
```

Additional algorithms may be added.

---

# 7. Random Search

Purpose

Generate random layouts.

```
Layout

↓

Random Swap

↓

Evaluate

↓

Keep Best
```

Advantages

- Simple
- Fast
- Baseline

Disadvantages

- Inefficient

---

# 8. Hill Climbing

```
Current

↓

Neighbor

↓

Better?

↓

Accept
```

Only better layouts are accepted.

Advantages

- Fast

Disadvantages

- Local optimum

---

# 9. Beam Search

Maintains

```
Top N layouts
```

instead of one.

```
Beam

↓

Expand

↓

Evaluate

↓

Keep Top N
```

Recommended

```
Beam Width

50

～

500
```

---

# 10. Simulated Annealing

Accepts worse layouts probabilistically.

```
Current

↓

Mutation

↓

Score Difference

↓

Probability

↓

Accept
```

Temperature decreases over time.

```
High Temperature

↓

Exploration

↓

Low Temperature

↓

Exploitation
```

---

# 11. Genetic Algorithm

Population

↓

Selection

↓

Crossover

↓

Mutation

↓

Evaluation

↓

Next Generation

Typical parameters

Population

```
100
```

Mutation Rate

```
2%

～

5%
```

Elite

```
5%
```

---

# 12. Mutation Operators

Supported mutations.

```
Swap

Rotate

Layer Move

Modifier Move

Combo Move

Symbol Rotation

Vowel Rotation

Consonant Rotation
```

Mutations should preserve validity.

---

# 13. Swap Mutation

```
A

↓

B

↓

Swap
```

Most common mutation.

---

# 14. Rotation Mutation

Example

```
A

↓

S

↓

D

↓

F

↓

A
```

Useful for local optimization.

---

# 15. Layer Mutation

Moves keys between

```
L0

L1

L2

L3
```

while respecting constraints.

---

# 16. Combo Mutation

Moves

```
Combo

Leader

Tap Dance

Macro
```

to alternative positions.

---

# 17. Neighborhood Definition

Neighbor layouts differ by

```
One Swap

or

One Rotation
```

Used by

Hill Climbing

Beam Search

Annealing

---

# 18. Acceptance Function

Hill Climbing

```
Better only
```

Annealing

```
Always Better

Sometimes Worse
```

Genetic

```
Population Ranking
```

---

# 19. Constraint Checking

Executed before evaluation.

Checks

```
Duplicate Keys

Missing Keys

Layer Limits

Modifier Limits

Finger Limits

Shortcut Rules
```

---

# 20. Finger Load Budget

Each finger has a maximum workload.

Example

| Finger | Budget |
|---------|--------|
| Index | 30% |
| Middle | 25% |
| Ring | 20% |
| Pinky | 15% |
| Thumb | 10% |

Penalty

```
Usage

>

Budget

↓

Penalty
```

---

# 21. Shortcut Constraints

Required shortcuts.

```
Ctrl+C

Ctrl+V

Ctrl+X

Ctrl+Z

Ctrl+A

Ctrl+S

Ctrl+F
```

Optional

IDE shortcuts

Gaming shortcuts

Terminal shortcuts

---

# 22. Harmonia Constraints

Specific constraints.

```
AIUEO Placement

Home Row Modifier

Thumb Layer

Combo Dependency

Programming Symbols
```

These constraints distinguish Harmonia optimization from general layout optimization.

---

# 23. Multi-objective Optimization

The optimizer minimizes

```
Finger Load

Travel

Same Finger

Learning Cost
```

while maximizing

```
Roll

Alternation

Programming

Shortcut

Language Score
```

Overall

```
Weighted Score
```

---

# 24. Pareto Optimization (Future)

Instead of one score,

maintain

```
Pareto Front
```

Example

```
Programming ↑

↓

Travel ↓

↓

Learning Cost ↓
```

Users choose preferred trade-offs.

---

# 25. Evaluation Cache

Avoid repeated evaluation.

```
Layout Hash

↓

Dictionary

↓

Cached Score
```

Reduces runtime significantly.

---

# 26. Parallel Processing

Independent layouts evaluated simultaneously.

Supports

```
ThreadPool

ProcessPool

Future

GPU
```

---

# 27. Random Seed

Every optimization run records

```
Seed

Algorithm

Parameters

Timestamp
```

Ensures reproducibility.

---

# 28. Stopping Conditions

Optimization ends when

```
Maximum Iterations

or

Target Score

or

No Improvement

or

Time Limit
```

is reached.

---

# 29. Benchmark Suite

Every algorithm is compared using

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

Metrics

```
Best Score

Runtime

Memory

Iterations
```

---

# 30. Logging

Each optimization step records

```
Iteration

Algorithm

Mutation

Score

Accepted

Best Score
```

Supports

Markdown

CSV

JSON

---

# 31. Future Algorithms

Candidate algorithms

```
Tabu Search

Ant Colony Optimization

Particle Swarm Optimization

Differential Evolution

Bayesian Optimization

Monte Carlo Tree Search

Reinforcement Learning
```

---

# 32. Harmonia Optimization Strategy

Optimization occurs in stages.

```
Stage 1

Hard Constraints

↓

Stage 2

AIUEO Optimization

↓

Stage 3

Finger Load Budget

↓

Stage 4

Same Finger Reduction

↓

Stage 5

Roll Optimization

↓

Stage 6

Programming Optimization

↓

Stage 7

Shortcut Optimization

↓

Stage 8

Layer Optimization

↓

Stage 9

Fine Tuning
```

This staged optimization improves convergence speed compared with optimizing all objectives simultaneously.

---

# 33. Recommended Optimization Workflow

The recommended workflow for Harmonia is:

```
Initial Layout
      │
      ▼
Random Search
      │
      ▼
Beam Search
      │
      ▼
Hill Climbing
      │
      ▼
Simulated Annealing
      │
      ▼
Genetic Algorithm
      │
      ▼
Fine Tuning
      │
      ▼
Benchmark
      │
      ▼
Final Layout
```

Each algorithm refines the result of the previous stage.

---

# 34. Future Research

Future topics.

```
Personalized Optimization

Adaptive Finger Budget

AI-assisted Layout Generation

Typing Habit Learning

Eye Tracking

EMG Integration

Typing Fatigue Prediction

Multi-user Optimization
```

---

# 35. Design Principles

The optimization engine shall satisfy:

- Algorithm-independent evaluation
- Reproducible results
- Configurable constraints
- Extensible architecture
- Parallel execution support
- Benchmark comparability

---

# End of Algorithm.md