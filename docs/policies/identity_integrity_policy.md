# Identity Integrity Policy

## Purpose

Define the identity model for CorporateAction workflow instances.

This policy ensures that workflow operations consistently act upon a unique action identity.

---

## Identity Rule 1

Each CorporateAction shall possess a unique:

```text
action_id
```

The action_id is the authoritative identifier for the workflow instance.

---

## Identity Rule 2

Workflow operations shall use only:

```text
action_id
```

for identity resolution.

Examples include:

- Updates
- Processing
- Retry handling
- Completion handling
- Failure handling
- Dead-letter processing

---

## Identity Rule 3

Duplicate action identities represent a persistence integrity failure.

They are not considered:

- Business rule violations
- Workflow validation failures
- Processor failures

---

## Identity Rule 4

Workflow history remains attached to the action_id for the entire lifecycle.

This includes:

- Status transitions
- Retry counts
- Processor outcomes
- Dead-letter outcomes

---

## Engineering Purpose

This policy guarantees:

- Deterministic workflow behavior
- Reliable update operations
- Reliable retry handling
- Reliable processor ownership
- Persistence integrity

Identity integrity is foundational to the workflow architecture.