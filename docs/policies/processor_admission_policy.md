# Processor Admission Policy

## Purpose

Determine whether a persisted CorporateAction is eligible for processor pickup and execution.

The queue contains the complete persisted work inventory.

This policy determines which actions are eligible for execution.

---

## Admission Rule 1

Actions in:

```text
VALIDATED
```

are eligible for processor pickup.

Processor pickup causes:

```text
VALIDATED
    ↓
PROCESSING
```

---

## Admission Rule 2

Actions in:

```text
RETRY_PENDING
```

are eligible for processor pickup.

Processor pickup causes:

```text
RETRY_PENDING
    ↓
PROCESSING
```

---

## Admission Rule 3

All statuses not explicitly listed above are ineligible for processor pickup.

---

## Processor Candidate Set

The processor may only select actions in:

```text
VALIDATED
RETRY_PENDING
```

All other statuses are excluded from execution consideration.

---

## Purpose Of This Policy

This policy prevents:

- Duplicate execution
- Premature execution
- Execution of terminal-state actions
- Execution of governance-failed actions

while ensuring workflow-approved actions can proceed.