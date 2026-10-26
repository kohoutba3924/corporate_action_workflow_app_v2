# Processing Readiness Policy

## Purpose

Determine whether a CorporateAction is eligible to transition from:

```text
RECEIVED
    ↓
VALIDATED
```

This policy governs readiness for workflow execution.

---

## Readiness Rule 1

### Action Must Exist In Persistence

Validation operates only on actions that have already been successfully persisted.

---

## Readiness Rule 2

### Domain Integrity Must Pass

The action must be loadable as a valid CorporateAction.

This includes all Phase 1 domain validation:

- Valid action type
- Valid metadata
- Valid metadata discriminator
- Valid date relationships
- Action type and metadata type alignment

This rule primarily protects against:

- Corrupted persistence data
- Manual file modifications
- Legacy migration issues
- Future schema changes

---

## Readiness Rule 3

### Action Must Be In RECEIVED Status

Only actions currently in:

```text
RECEIVED
```

may undergo readiness validation.

---

## Validation Outcomes

### Success

```text
RECEIVED
    ↓
VALIDATED
```

The action is eligible for processor pickup.

---

### Failure

```text
RECEIVED
    ↓
DEAD_LETTER
```

The action is not eligible for workflow progression.

---

## Governance Classification

Readiness validation failures are governance failures.

They are:

- Not processor failures
- Not retryable failures

Manual review and remediation are required.