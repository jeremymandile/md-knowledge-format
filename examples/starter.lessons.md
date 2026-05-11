---
lessons_version: "1.0"
created: "2025-01-01"
project: "my-agent-project"
---

# Lessons Learned

## DO NOT

### DO NOT use `pandas.DataFrame.append`
- **Why:** Deprecated in pandas 1.4.0, removed in 2.0.
- **Use instead:** `pd.concat([df, new_row_df], ignore_index=True)`
- **First seen:** 2025-01-01 (agent: data-cruncher)
- **Tags:** #pandas #deprecation #data

### DO NOT query `transactions` without a `READONLY` hint on replicas
- **Why:** Causes table locks on the primary, impacting production performance.
- **Use instead:** `/* READONLY */ SELECT ... FROM transactions_replica ...`
- **First seen:** 2025-01-01 (agent: report-gen)
- **Tags:** #sql #production #safety

## PITFALLS

### `datetime.now()` is not timezone-aware inside containers
- **What happens:** The container runs in UTC but the value is treated as local time.
- **Fix:** Use `datetime.now(timezone.utc)` or `pendulum.now()`
- **Context:** Any cron-based or scheduled agent.
- **Tags:** #python #timezone #containers

## SUCCESS PATTERNS

### Chain-of-draft reasoning before writing more than 50 lines of code
- **Result:** Reduced review cycles by ~30 %.
- **How:** Agent writes a numbered plain-language outline first, then implements.
- **Tags:** #process #code-gen
