---
paths:
  - "pricing.py"
  - "**/pricing*.py"
---

# Pricing rules

- All money is stored and computed as **integer cents**. Never use `float`
  for money; convert to a display string only at the edge (CLI output).
- Percentage discounts round **half up** to the nearest cent.
- Every new pricing function needs at least one pytest test, including a
  rounding edge case.
