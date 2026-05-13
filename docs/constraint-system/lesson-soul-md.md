# lesson-soul-md.md

## SOUL.md: Identity Conditioning Layer Specification

---

## 1. Purpose

SOUL.md defines a persistent behavioral conditioning layer for an AI agent.
It does not encode procedures, tasks, or workflows.
It biases how all other instructions are interpreted and expressed.

Primary function:
Apply a stable, global prior over tone, epistemic stance, verbosity, and conversational behavior.

It is not a policy engine, not executable logic, not a sequential processing stage.
It is a conditioning input that acts concurrently with all other constraints.

---

## 2. Position in the Constraint System

SOUL.md does not execute "before" or "after" LESSON.md or system policy.
All constraints act simultaneously on a shared decoding process.

The dependency graph is organizational, not temporal:

```
System Policy   ─┐
SOUL.md          ├──→  Shared Decoding Process  →  Output
LESSON.md       ─┘
Runtime Context  ─┘
```

SOUL.md does not override system policy.
It biases the probability distribution from which output is sampled,
while other constraints define the space of allowable samples.

> Explicit: SOUL.md does not execute in sequence with LESSON.md;
> both act concurrently as conditioning inputs to a single decoding process.

---

## 3. Functional Model

SOUL.md operates as a probabilistic conditioning prior over output generation.

Let:

* I = set of active instructions (system + lesson + runtime context)
* S = SOUL.md constraints (behavioral prior)
* O = generated output

Then:

O ~ P(token | I, S)

Where S shifts the distribution over:

* lexical choice
* verbosity
* hedging frequency
* assertiveness level
* response structure preference
* conversational tone

S does not add capabilities. It does not define valid outputs.
It makes some already-valid outputs more probable than others.

---

## 4. Scope of Influence

SOUL.md influences:

* Tone (formal, neutral, blunt, informal)
* Epistemic posture (certainty expression, hedging frequency)
* Verbosity (compression vs elaboration bias)
* Pragmatic stance (directness, willingness to critique)
* Interaction style (proactive vs reactive framing)

SOUL.md does NOT define:

* task execution steps
* tool usage logic
* safety policy behavior
* factual knowledge base
* structured workflows

---

## 5. Constraint Semantics

SOUL.md constraints are:

* concurrent (not sequential — act alongside other constraints during decoding)
* global (apply to all outputs)
* persistent (do not reset per turn)
* probabilistic (bias, not rule enforcement)
* subordinate to system-level constraints

Conflicting SOUL.md instructions do not fail explicitly;
they degrade coherence or are probabilistically neutralized.

---

## 6. Instruction Collision Model

SOUL.md and other instruction sets interact through weighted constraint resolution
within a single decoding step.

Common collision classes:

### 6.1 Tone vs Safety

* bluntness vs harm-avoidance framing
* resolved by system policy dominance

### 6.2 Brevity vs Completeness

* compression pressure vs informational sufficiency
* resolved contextually based on task complexity

### 6.3 Confidence vs Accuracy

* assertive stance vs uncertainty representation
* resolved toward calibrated hedging under uncertainty

### 6.4 Personality vs Procedural Constraints

* stylistic directives vs step-by-step requirements
* procedural invariants override stylistic constraints for structure-critical tasks

---

## 7. Failure Modes

### 7.1 Over-specification

Excessively detailed SOUL.md definitions reduce effectiveness by:

* competing with procedural instructions in the same decoding step
* increasing instruction entropy
* reducing stable behavioral bias

### 7.2 Contradictory constraints

Example:

* "be extremely concise"
* "always be highly detailed"

Effect:

* oscillation in verbosity
* inconsistent response structure

### 7.3 Policy interference

When SOUL.md conflicts with system-level constraints:

* SOUL.md is partially ignored or neutralized
* no explicit error is produced

### 7.4 Persona fragmentation

Occurs when SOUL.md attempts to encode multiple incompatible personas.

Result:

* unstable tone shifts
* inconsistent epistemic stance

---

## 8. Design Constraints

SOUL.md should be:

* small (high signal density)
* non-procedural
* non-operational
* non-redundant with LESSONS.md
* free of task-specific logic

SOUL.md should NOT include:

* workflows
* tool instructions
* step-by-step procedures
* system prompts
* policy text
* large descriptive narratives

---

## 9. Interaction with LESSON.md

SOUL.md and LESSON.md act concurrently on the same decoding process.
Neither executes "before" or "after" the other.

Relationship:

* SOUL.md = behavioral prior (shifts probability within valid space)
* LESSON.md = structural constraints (defines valid space)

LESSON.md defines what outputs are acceptable.
SOUL.md biases which acceptable outputs are generated.

---

## 10. Stability Principle

The effectiveness of SOUL.md is inversely correlated with complexity.

Let:

* C = complexity of SOUL.md content
* E = stability of behavioral conditioning

Then:

E ∝ 1 / C

Optimal SOUL.md design minimizes complexity while maximizing behavioral leverage.

---

## 11. Summary Definition

SOUL.md is a persistent, concurrent probabilistic conditioning prior
that shapes global response characteristics without defining tasks or procedures.
It acts simultaneously with all other constraints on a shared decoding process,
biasing—not determining—the output distribution.
