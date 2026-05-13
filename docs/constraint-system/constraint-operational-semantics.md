# constraint-operational-semantics.md

## Operational Semantics of Concurrent Constraint Systems Under Attention Window Partitioning

---

## 1. Purpose

This document defines how constraint systems (H, Lₛ, Lₚ, S, R) are actually
applied during decoding in transformer-based agents under finite context windows.

It does not redefine constraint classes. It defines execution behavior under
attention limits, truncation, and token-local computation.

This is the layer missing from most theoretical constraint models: not what
constraints mean, but how they survive computation.

---

## 2. Core Reality: Windowed Computation

Transformers do not evaluate full instruction sets globally.

They operate on a bounded attention window W(t) at each decoding step t.

Let:

- W(t) = active context window at token position t
- C = full constraint set {H, Lₛ, Lₚ, S, R}
- C ∩ W(t) = constraints visible at step t

Then:

```
EffectiveConstraints(t) = project(C ∩ W(t))
```

Only constraints inside W(t) can influence token t.

---

## 3. Constraint Visibility vs Constraint Existence

A critical distinction:

- **Existence**: constraint is present in context
- **Visibility**: constraint is inside attention window W(t)

Formally:
- If c ∉ W(t): c is *inactive* at t
- If c ∈ W(t): c is *active* at t

This produces a structural phenomenon:

> Constraint systems are temporally non-stationary even when logically static.

---

## 4. Window Partition Model

At any token position t, the model sees three regions:

```
[ Global context (partially visible) ]
[ Local window W(t)                  ]
[ Future-unseen region               ]
```

Only W(t) is fully operational.

### 4.1 Zone A — Fully active constraints

Inside W(t), fully attended.
- High enforcement fidelity
- All constraint classes active (H, Lₛ, Lₚ, S, R)

### 4.2 Zone B — Partially attenuated constraints

Inside context but low attention weight.
- S and R degrade first
- Lₛ and Lₚ degrade slowly
- H remains invariant if represented

Primary source of drift, inconsistency across long outputs, and "forgotten earlier instructions."

### 4.3 Zone C — Invisible constraints

Outside W(t).
- Treated as non-existent at time t
- May reappear later if window shifts

---

## 5. Constraint Survival Function

Define survival probability of constraint c at position t:

```
P(survive c, t) = f(distance(c, W(t)), type(c))
```

Where:
- distance = token distance from attention center
- type = H, Lₛ, Lₚ, S, R

Empirical ordering of stability:

```
H > Lₛ > Lₚ > S > R
```

Interpreted as persistence under truncation, not authority.

---

## 6. Decay Dynamics

Each constraint class has a decay curve over distance d:

### 6.1 Hard constraints (H)

```
P(decay) ≈ 0
```

Only fail if not represented in window or structurally malformed.

### 6.2 Structural constraints (Lₛ)

```
P(decay) ~ log(d)
```

Slow degradation. Failure mode: schema drift, format inconsistency, partial omission of required sections.

### 6.3 Procedural constraints (Lₚ)

```
P(decay) ~ linear(d)
```

Medium degradation. Failure mode: step reordering, skipped reasoning steps, compressed workflows.

### 6.4 Behavioral priors (S)

```
P(decay) ~ exponential(d)
```

Fast degradation. Failure mode: tone reversion to base model, loss of stylistic consistency, "personality collapse."

### 6.5 Runtime context (R)

```
P(decay) ~ super-exponential(d)
```

Immediate degradation. Failure mode: forgetting tool outputs, ignoring recent retrieval, local hallucination dominance.

---

## 7. Attention Allocation Constraint

At each token, attention budget A is finite:

```
A = A(H) + A(Lₛ) + A(Lₚ) + A(S) + A(R)
∑ A(i) ≤ capacity(W(t))
```

This forces competition. Constraint systems are not only competing logically—they are competing for attention mass.

---

## 8. Attention Competition Rule

When capacity is exceeded, allocation priority:

```
H → Lₛ → Lₚ → S → R
```

Degradation is compression of representation fidelity, not removal:
- H: preserved fully or fails catastrophically
- Lₛ: compressed but preserved structurally
- Lₚ: partially elided steps
- S: averaged tone drift
- R: dropped entirely or hallucinated

---

## 9. Window Shift Effects

As decoding progresses: W(t) → W(t+1)

This causes:
- **Constraint reactivation**: previously invisible constraints re-enter window → sudden "corrections"
- **Constraint disappearance**: previously active constraints exit window → silent drift

This explains mid-response contradiction repair, late-answer format correction, and sudden tone shifts. Not stochastic error—deterministic window movement effect.

---

## 10. SOUL × LESSON Interaction Under Window Pressure

Inside full window (W large):
- S and Lₛ/Lₚ coexist cleanly → stable behavior

Under shrinking window:
1. S collapses first → tone reversion
2. Lₚ fragments → procedural loss
3. Lₛ compresses → structure preserved but simplified
4. H dominates remaining space → safety/validity remains

Result: Outputs become structurally correct but stylistically flattened under pressure.

---

## 11. Long-Context Drift Mechanism

Long-context degradation is not memory loss. It is constraint de-weighting due to window recentering bias.

As W(t) shifts forward:
- Early constraints move out of high-attention region
- Their effective weight decays
- Later constraints dominate decoding

Produces inconsistency in tone across long outputs, loss of early instructions, and gradual structural simplification.

---

## 12. Stability Condition (Revised)

System stability requires:

```
∀ t: H ⊆ W(t)
and
rank(Lₛ) + rank(Lₚ) + rank(S) + rank(R) ≤ A
```

Where:
- H must always remain in window (explicit anchoring requirement)
- Non-hard constraints must fit within attention budget

Failure to satisfy this produces silent constraint dropout, not explicit errors.

---

## 13. Key Insight

Constraint systems are not "evaluated." They are reweighted under shifting attention geometry.

All observed failures (drift, inconsistency, loss of personality) are not logic errors. They are window exclusion artifacts, attention reallocation artifacts, and decay-based constraint degradation.

---

## 14. Relationship to Precedence Algebra

The precedence algebra defines **logical dominance**. This document defines **temporal survival under computation**. They are orthogonal layers:

- Algebra = static resolution model
- Operational semantics = dynamic execution model

---

## 15. Final Model Statement

Agent behavior is the result of:

```
Constraint resolution (algebra)
×
Attention window survival dynamics (semantics)
```

Not sequence. Not pipeline. Not hierarchy. But continuous re-evaluation of a constrained probabilistic system under finite and shifting attention capacity.
