# Retry Policy

## Purpose

Define recovery behavior following processing failures.

This policy applies only to execution failures.

It does not apply to validation failures.

---

## Scope

Applies to:

```text
PROCESSING
    ↓
FAILED
```

Does not apply to:

```text
RECEIVED
    ↓
DEAD_LETTER
```

Validation failures are governance failures and are not retryable.

---

## Retry Rule 1

Only actions in:

```text
FAILED
```

are eligible for retry evaluation.

---

## Retry Rule 2

Each action maintains a:

```text
retry_count
```

that tracks the number of processing retries attempted.

---

## Retry Rule 3

Maximum retry count:

```text
3
```

---

### Retry Allowed

If:

```text
retry_count < 3
```

transition:

```text
FAILED
    ↓
RETRY_PENDING
```

---

### Retry Exhausted

If:

```text
retry_count >= 3
```

transition:

```text
FAILED
    ↓
DEAD_LETTER
```

---

## Retry Rule 4

The processor handles:

```text
VALIDATED
```

and

```text
RETRY_PENDING
```

using the same execution process.

Processor pickup transitions:

```text
RETRY_PENDING
    ↓
PROCESSING
```

---

## Retry Rule 5

Successful retry execution results in:

```text
PROCESSING
    ↓
COMPLETED
```

and exits the retry lifecycle.

---

## Retry Rule 6

Dead-lettered actions require:

- Manual review
- Manual remediation

No further automatic retries shall occur.

---

## Retry Lifecycle Example

```text
VALIDATED
    ↓
PROCESSING
    ↓
FAILED
    ↓
RETRY_PENDING
    ↓
PROCESSING
    ↓
FAILED
    ↓
RETRY_PENDING
    ↓
PROCESSING
    ↓
FAILED
    ↓
DEAD_LETTER
```