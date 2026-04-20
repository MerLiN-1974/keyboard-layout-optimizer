# Keyboard Layout Optimization using Simulated Annealing

## Overview

This project explores how keyboard layouts impact typing effort by modeling typing as a geometric optimization problem.

Using **Simulated Annealing**, the system searches for improved keyboard layouts that minimize the total finger travel distance for a given text corpus.

---

## Problem Formulation

* Each key is assigned a fixed coordinate (QWERTY-style grid)
* A **layout** is a mapping from characters → coordinates
* Given a text, define cost as:
  
$$
\text{Cost} = \sum_{i=1}^{n-1} \text{distance}(c_i, c_{i+1})
$$

* Distance is Euclidean

---

## Objective

Minimize total typing cost by optimizing character-to-key assignments while keeping physical key positions fixed.

---

## Approach

### 1. Initialization

* Start with standard QWERTY mapping

### 2. Neighbor Generation

* Randomly swap positions of two characters

### 3. Cost Evaluation

* Compute total path length over text

### 4. Acceptance Rule

* Always accept better solutions
* Accept worse solutions with probability:
  
$$
P = e^{-\Delta / T}
$$
### 5. Cooling Schedule

* Temperature decays geometrically:
  
$$
T \leftarrow \alpha \cdot T
$$

---

## Features

* Configurable annealing parameters (iterations, temperature, decay)
* Supports both file input and inline text
* Generates:

  * optimized keyboard layout (JSON)
  * cost convergence plots
  * final layout visualization

---

## Results

The optimizer consistently reduces typing cost compared to the QWERTY baseline.

Example output:

* Baseline cost: X
* Optimized cost: Y
* Improvement: Δ

---

## Visualizations

### Cost Convergence

Shows how the optimization progresses over time.

### Final Layout

Displays optimized key positions on the keyboard grid.

---
## Setup

```bash
pip install -r requirements.txt
```
## How to Run

```bash
python3 main.py --file sample_text.txt
```

### Optional arguments:

```bash
--iters 50000
--t0 1.0
--alpha 0.999
--epoch 1
```

---

## Code Structure

* `simulated_annealing()` → core optimization loop
* `path_length_cost()` → objective function
* `swap_two()` → neighborhood generation
* `plot_costs()` → visualization

---

## Design Choices

* Euclidean distance approximates typing effort
* Simplified “single-finger” model for tractability
* Simulated annealing used for escaping local minima

---

## Limitations

* Does not model real finger ergonomics
* Ignores multi-finger typing dynamics
* Depends on input text distribution

---

## Future Work

* Model finger assignments and home-row constraints
* Use bigram/trigram frequency weighting
* Compare with genetic algorithms or hill climbing

---

## Motivation

This project demonstrates:

* heuristic search
* modeling real-world systems with simplifications

It serves as a practical example of applying optimization techniques to human-computer interaction problems.
