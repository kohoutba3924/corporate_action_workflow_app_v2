# Workflow State Transition Policy

## Purpose

Define the authoritative workflow lifecycle for a CorporateAction and govern all permitted state transitions.

This policy establishes:

- Status meanings
- Allowed transitions
- Forbidden transitions
- Terminal states
- Validation failure handling

---

## Status Definitions

### RECEIVED

The action has been accepted into the system and successfully persisted.

Characteristics:

- Exists in persistence storage.
- Exists in the queue inventory.
- Has not yet passed operational validation.
- Not eligible for processing.

---

### VALIDATED

The action has passed all operational validation checks.

Characteristics:

- Eligible for processor pickup.
- Ready for execution.
- No known workflow governance violations.

---

### PROCESSING

The action is actively being processed.

Characteristics:

- Processor owns the action.
- Must not be processed concurrently.
- May complete successfully.
- May fail.

---

### COMPLETED

The action has been successfully processed.

Characteristics:

- Terminal state.
- No further processing allowed.

---

### FAILED

Processing was attempted and failed.

Characteristics:

- Failure has been recorded.
- Awaiting retry evaluation.

---

### RETRY_PENDING

A failed action has been approved for retry.

Characteristics:

- Eligible for future processor pickup.
- Retry count tracked separately.

---

### DEAD_LETTER

The action cannot continue through automated processing.

Characteristics:

- Terminal state.
- Requires manual review and remediation.

---

## Allowed Transitions

```text
RECEIVED
    ↓
VALIDATED

RECEIVED
    ↓
DEAD_LETTER

VALIDATED
    ↓
PROCESSING

PROCESSING
    ↓
COMPLETED

PROCESSING
    ↓
FAILED

FAILED
    ↓
RETRY_PENDING

FAILED
    ↓
DEAD_LETTER

RETRY_PENDING
    ↓
PROCESSING
```

---

## Forbidden Transitions

Any transition not explicitly listed in the Allowed Transitions section is prohibited.

Examples include:

```text
RECEIVED     → PROCESSING
RECEIVED     → COMPLETED

VALIDATED    → COMPLETED
VALIDATED    → FAILED

COMPLETED    → ANYTHING

DEAD_LETTER  → ANYTHING

PROCESSING   → RECEIVED
PROCESSING   → VALIDATED
```

---

## Terminal States

The following states are terminal:

```text
COMPLETED
DEAD_LETTER
```

Actions in terminal states may not transition further.

---

## Validation Failure Handling

Validation failures are governance failures.

Validation failures transition:

```text
RECEIVED
    ↓
DEAD_LETTER
```

and require manual review and remediation.