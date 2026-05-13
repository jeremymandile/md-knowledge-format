# constraint-precedence-algebra.md

## Constraint Precedence Algebra for Concurrent Agent Instruction Systems

---

## 1. Purpose

This document defines a formal model for resolving conflicts between
concurrent instruction fields in agent systems.

It applies to systems with:

- System Policy constraints (hard, non-overridable)
- SOUL.md (behavioral prior / probabilistic conditioning)
- LESSON.md (structural constraints + procedural constraints)
- Runtime context (tools, memory, retrieval)

It does NOT assume sequential execution.
All constraints act concurrently on a shared decoding process.

The goal is not to eliminate conflict—conflict is inherent in any system with
multiple constraint sources. The goal is to make conflict resolution
predictable, auditable, and stable under load.

---

## 2. Core Model

Let:

- P₀ = base model distribution
- H = System policy hard constraints (inviolable set)
- Lₛ = LESSON.md structural constraints (format, schema, admissibility)
- Lₚ = LESSON.md procedural constraints (ordering, workflows, steps)
- S = SOUL.md constraint field (behavioral prior)
- R = runtime context constraints (tools, state, retrieval)

Then generation is defined as:

```
O ~ P(token | P₀, H, Lₛ, Lₚ, S, R)
```

Where:

- H defines the *valid output space boundary*
- Lₛ defines *structural admissibility* (what form is acceptable)
- Lₚ defines *procedural ordering* (what sequence is acceptable)
- S reshapes *probability distribution over admissible outputs*
- R dynamically conditions local token-level state

No term is temporally ordered. All act simultaneously on a single decoding step.

---

## 3. Constraint Classification

Every instruction—whether sourced from SOUL.md, LESSON.md, system policy, or
runtime context—is assigned exactly one constraint class.

### 3.1 Class A: Hard Invariants (H)

Must always hold. Violation is a system‑level failure.

Properties:
- absolute
- non-negotiable
- prune invalid token paths

Examples:
- "Do not output user PII."
- "Validate tool output before use."
- Safety policies, system‑level refusals.

Effect:
```
P(x) = 0 if x ∉ H
```

Behavior: Overrides all other constraint classes unconditionally.

### 3.2 Class Bₛ: Structural Constraints (Lₛ)

Define the admissible structure space. They specify *what form* output must take.

Source: LESSON.md structural rules (schemas, formats, required sections).

Properties:
- categorical (valid/invalid structural types)
- define output manifold shape
- enforce format invariants

Examples:
- "Output must be valid JSON."
- "Must include YAML front matter."
- "Code blocks must specify language."

Effect:
```
Lₛ restricts support of P₀ ∩ H to structurally admissible forms
```

Behavior: Cannot be overridden by S. Can only be reshaped in expression,
not in substance.

### 3.3 Class Bₚ: Procedural Constraints (Lₚ)

Define the admissible sequence space. They specify *what order* steps must follow.

Source: LESSON.md procedural rules, workflow definitions.

Properties:
- ordering constraints
- step dependencies
- execution invariants

Examples:
- "Always validate input before calling a tool."
- "Cite sources before drawing conclusions."
- "Use pd.concat(), not DataFrame.append."

Effect:
```
Lₚ restricts support of P₀ ∩ H to procedurally valid sequences
```

Behavior: Can be reshaped by S in expression (e.g., compressed, rephrased)
but not in substance (steps cannot be reordered or skipped).

### 3.4 Class C: Behavioral Priors (S)

Shape probability distribution over valid outputs. Do not define what is
acceptable; only bias which acceptable output is generated.

Source: SOUL.md.

Properties:
- probabilistic
- non-restrictive
- distribution-shaping

Examples:
- "Be blunt."
- "Skip filler."
- "Never open with 'Great question.'"

Effect:
```
S reweights P(x | H ∩ Lₛ ∩ Lₚ)
```

S does NOT remove valid outputs; it changes likelihood.

Behavior: Operates entirely within the space defined by Class A, Bₛ, and Bₚ
constraints. Cannot override a higher‑precedence constraint. Can be fully
neutralized if local context demands it.

### 3.5 Class D: Contextual Heuristics (R)

Lowest‑priority guidance. Fallbacks, preferences, defaults.

Source: Runtime context, conversation state, user preferences.

Properties:
- dynamic
- ephemeral
- token-local influence

Examples:
- "If unsure, ask a clarifying question."
- "Prefer tables over lists for comparisons."
- "Default to metric units."

Effect:
```
R conditions local probability shifts during decoding
```

Behavior: Applied only when no Class A, Bₛ, Bₚ, or C constraint is active
at the decision point. First constraint to degrade under load.

---

## 4. Precedence Rules

### 4.1 Precedence is NOT Sequential

No constraint executes before another.
Precedence is class‑based dominance, not temporal ordering.

### 4.2 Absolute Precedence

```
Class A (Hard Invariants)
  ↓ overrides
Class Bₛ (Structural Constraints)
  ↓ overrides
Class Bₚ (Procedural Constraints)
  ↓ overrides
Class C (Behavioral Priors)
  ↓ overrides
Class D (Contextual Heuristics)
```

Resolution:
- If constraints of different classes conflict at a token position, the
  higher‑precedence class wins unconditionally.
- If multiple constraints of the same class conflict, apply the class‑specific
  resolution rule (see §5).

### 4.3 Transitivity

Precedence is transitive:

```
A > Bₛ > Bₚ > C > D
```

No cycles are possible by construction.

### 4.4 Non‑Overlap by Design

The constraint classification system is deliberately coarse—five classes—to
prevent ambiguity. If a constraint cannot be unambiguously classified, it is
either:

- Decomposed into separate Class A, Bₛ, Bₚ, C, or D components, or
- Rejected as malformed.

---

## 5. Same‑Class Conflict Resolution

### 5.1 Class A Conflict

Class A constraints cannot conflict by design.
If two Class A constraints appear to conflict, one is misclassified.
Resolution: reclassify the softer constraint as Bₛ or Bₚ.

### 5.2 Class Bₛ Conflict

When two structural constraints conflict:

- The constraint appearing **earlier in the loaded instruction set** wins
  (stable ordering via file position, not stochastic).

### 5.3 Class Bₚ Conflict

When two procedural constraints conflict:

- If one is a dependency prerequisite (must happen first), it wins.
- If both are same‑priority, the constraint appearing **earlier in the loaded
  instruction set** wins.

### 5.4 Class C Conflict

When two SOUL.md priors conflict (e.g., "be concise" and "be detailed"):

- Neither "wins" deterministically.
- The model resolves probabilistically per token region.
- This is the primary source of persona fragmentation.

Mitigation: Class C conflicts should be eliminated at authoring time, not
resolved at runtime. The author is responsible for ensuring SOUL.md does not
contain contradictory priors.

### 5.5 Class D Conflict

When two heuristics conflict, the one with higher local context relevance wins.
Relevance is determined by:

- Recency (newer instruction within the context window)
- Specificity (more specific to the current task)
- Source authority (user override > system default)

---

## 6. Collision Resolution Algorithm

For a given token position t with active constraints {C₁, C₂, ..., Cₙ}:

```
function resolve(t, active_constraints):
    // 1. Group by class
    A  = constraints of class A  active at t
    Bs = constraints of class Bₛ active at t
    Bp = constraints of class Bₚ active at t
    C  = constraints of class C  active at t
    D  = constraints of class D  active at t

    // 2. Class A dominates unconditionally
    if A is non-empty:
        return A

    // 3. Class Bₛ resolves internally, then dominates
    if Bs is non-empty:
        return resolve_same_class(Bs, "Bₛ")

    // 4. Class Bₚ resolves internally, then dominates
    if Bp is non-empty:
        return resolve_same_class(Bp, "Bₚ")

    // 5. Class C resolves probabilistically
    if C is non-empty:
        return sample_from(C)

    // 6. Class D resolves heuristically
    if D is non-empty:
        return resolve_same_class(D, "D")

    // 7. No active constraints — default model behavior
    return unconstrained_decode()
```

---

## 7. Substance vs Expression Boundary

A critical distinction for SOUL × LESSON interaction:

- **Substance** = constraint satisfaction condition (what must be true for
  the constraint to be fulfilled).
- **Expression** = realization pathway under a satisfied constraint (how
  the fulfilled constraint is communicated).

Rule:
> Class C (S) can reshape **expression** but cannot alter **substance**.

This makes the "no override" rule formally checkable:

- Lₛ substance: "Output must be valid JSON." → S cannot change this.
- Lₛ expression: S can influence indentation, key ordering, verbosity within JSON.
- Lₚ substance: "Validate before calling tool." → S cannot reorder or skip.
- Lₚ expression: S can make the validation step terse or verbose.

---

## 8. Unified Constraint Resolution Equation

Generation is:

```
P*(x) = normalize(
    P₀(x)
    constrained by H
    structured by Lₛ
    ordered by Lₚ
    biased by S
    conditioned by R
)
```

---

## 9. Dimensional Separation Principle

Each constraint class operates on an orthogonal axis:

| Constraint Class | Axis | Type |
|-----------------|------|------|
| A (H) | validity | binary |
| Bₛ (Lₛ) | structure | categorical |
| Bₚ (Lₚ) | procedure | ordinal/dependency |
| C (S) | probability | continuous |
| D (R) | locality | temporal window |

No two constraints operate on the same axis.
Lₛ and Lₚ are separated to preserve this invariant.

---

## 10. SOUL vs LESSON Interaction Model

### 10.1 Non-overlap invariant

```
Lₛ ∩ Lₚ defines support set Ω
S defines probability distribution over Ω
```

### 10.2 Invalid overlap condition

If SOUL attempts structural or procedural control:

```
Lₛ overrides S at structural axis
S collapses into stylistic variation within the admissible form
```

---

## 11. Formal Invariants

1. **No Class A violation**: Class A constraints are never violated.
2. **Class Bₛ substance preserved**: Structural constraints may be reshaped in expression but not in substance.
3. **Class Bₚ substance preserved**: Procedural constraints may be reshaped in expression but not in substance.
4. **Class C bounded**: SOUL.md priors operate entirely within the admissible space defined by Class A, Bₛ, and Bₚ.
5. **Class D first‑to‑degrade**: Heuristics are dropped before any other constraint class.
6. **No cross‑class cycling**: Precedence is acyclic by construction.
7. **Authoring responsibility for Class C conflicts**: The system does not resolve contradictory SOUL.md priors; the author must resolve them.
8. **Dimensional separation**: No two constraint classes operate on the same axis.

---

## 12. Key Invariant

> SOUL.md never determines what is valid.
> LESSON.md determines what structure is admissible and what sequence is acceptable.
> System policy determines what is possible.

---

## 13. Summary

The constraint precedence algebra decomposes all agent instructions into five
non‑overlapping classes (A: Hard Invariants, Bₛ: Structural, Bₚ: Procedural,
C: Behavioral Priors, D: Contextual Heuristics) and defines a transitive,
acyclic precedence order over them.

```
P*(x) = normalize(P₀(x) constrained by H, structured by Lₛ, ordered by Lₚ, biased by S, conditioned by R)
```

It does not attempt to eliminate conflict. It makes conflict resolution
predictable—deterministic for hard and structural classes (A, Bₛ, Bₚ),
probabilistic but bounded for style (C), and gracefully degradable for
heuristics (D).
