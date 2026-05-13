# failure-mode-taxonomy-multi-agent-interference.md

## Failure-Mode Taxonomy of Multi-Agent Interference (Fleet-Level SOUL Divergence)

---

## 1. Purpose

This document classifies emergent failure modes in multi-agent systems where:

- Each agent operates under a shared constraint algebra (H, Lₛ, Lₚ, S, R)
- SOUL.md priors are not globally synchronized across agents
- LESSON.md structures are partially shared or version-divergent
- Runtime contexts differ across execution instances

The primary failure axis is SOUL divergence under shared structural constraints.

---

## 2. Core Phenomenon: Fleet SOUL Divergence

Let:

- Sᵢ = SOUL.md state for agent i
- L = shared LESSON.md constraint set (possibly versioned)
- H = system policy (shared)
- Rᵢ = local runtime context

Fleet divergence occurs when:

```
∀ i, j: Sᵢ ≠ Sⱼ  ∧  L shared
```

This creates identical structure space, divergent behavioral priors.
Result: agents remain syntactically consistent but semantically drift apart.

---

## 3. Failure Mode Classes

### 3.1 FM-1: Tone Convergence Failure

Agents converge on similar structural outputs (Lₛ dominance), but SOUL divergence causes inconsistent tone distribution.

Symptoms: one agent terse, another verbose; one assertive, another hedged; output structures identical, phrasing diverges.

Mechanism: Lₛ alignment high, S divergence high.

Effect: perceived inconsistency in "personality coherence," misdiagnosed as model randomness.

### 3.2 FM-2: Structural Drift Synchronization Failure

Agents begin violating Lₛ in different ways under shared load.

Symptoms: schema inconsistencies across agents, JSON validity divergence, missing required sections in subsets of fleet outputs.

Mechanism: Lₛ overload under attention saturation; Class Bₛ degradation occurs unevenly across agents.

Result: partial structural collapse without global failure.

### 3.3 FM-3: Procedural Desynchronization

Agents execute Lₚ constraints in different interpreted orders.

Symptoms: tool calls occur in different sequences, validation steps skipped in some agents but not others, race-condition-like behavior across outputs.

Mechanism: Lₚ interpretation variance under Rᵢ differences.

Key property: not violation of constraints—divergent resolution of ambiguous procedural ordering.

### 3.4 FM-4: SOUL Overlap Collapse

Multiple SOUL.md priors collapse into indistinguishable behavioral regimes.

Symptoms: agents become stylistically identical, loss of intended personality differentiation, homogenized outputs across fleet.

Mechanism: Sᵢ differences below effective entropy threshold; behavioral prior compression under repeated prompting.

Result: fleet behaves like single-agent system with replicated structure.

### 3.5 FM-5: Constraint Shadowing

Lower-priority constraints appear inactive due to persistent dominance by higher classes.

Symptoms: Class C (S) appears ineffective, Class D never surfaces, only structural outputs visible.

Mechanism: H ∪ Lₛ ∪ Lₚ saturation → S and R suppressed.

This is not failure of S or R, but effective elimination by constraint density.

### 3.6 FM-6: Contextual Phase Desynchronization

Agents operating on different Rᵢ states diverge despite identical H, L, S.

Symptoms: different interpretations of same prompt, divergent use of retrieved memory, inconsistent tool invocation decisions.

Mechanism: Rᵢ divergence accumulates over time; local context windows drift independently.

### 3.7 FM-7: Feedback Amplification Loops

Small SOUL differences amplify through repeated agent interactions.

Symptoms: one agent becomes increasingly terse over time, another increasingly verbose, divergence grows non-linearly.

Mechanism:
```
Sᵢ(t+1) = Sᵢ(t) + f(outputᵢ(t))
```

Closed-loop reinforcement of behavioral priors.

---

## 4. Cross-Agent Interaction Failure Modes

### 4.1 FM-X1: Consensus Illusion

Agents appear to agree structurally (L alignment), but differ semantically due to S divergence.

Risk: false assumption of system-level agreement.

### 4.2 FM-X2: Cascading Constraint Misinterpretation

One agent's output becomes another agent's Lₚ input. If upstream agent degrades, downstream procedural interpretation becomes corrupted.

### 4.3 FM-X3: Fleet Polarization

SOUL divergence bifurcates into stable clusters: terse + structured vs. verbose + exploratory.

System becomes bimodal rather than unified.

---

## 5. Stability Conditions

Fleet is stable if:

```
Var(Sᵢ) < threshold
AND L consistency across agents ≈ 1.0
AND R divergence bounded
```

Instability emerges when:
- S variance grows faster than L variance is corrected
- R drift accumulates without reset
- Cross-agent outputs feed back into each other without normalization

---

## 6. Primary Root Cause Classification

All fleet-level failures reduce to one of three roots:

1. SOUL variance (S divergence)
2. Context drift (R divergence)
3. Structural saturation (L overload)

Everything else is a composite.

---

## 7. Key Invariant

> Multi-agent systems fail not by breaking constraints, but by allowing
> identical constraints to resolve differently under divergent priors.

---

## 8. Summary

Fleet-level SOUL divergence produces predictable failure modes: tone incoherence (FM-1), structural drift (FM-2), procedural desynchronization (FM-3), behavioral homogenization (FM-4), constraint shadowing (FM-5), context desynchronization (FM-6), and feedback amplification (FM-7).

All are emergent properties of shared L + divergent S + drifting R, not of model incapacity.
