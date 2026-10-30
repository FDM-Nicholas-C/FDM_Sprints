# Domain Model Notes

## Overview

The complaint-management domain contains four core models:

1. Customer
2. Account
3. Complaint
4. ComplaintStatusEvent

These models represent the business domain only and contain no SQL,
database code, FastAPI code, or infrastructure concerns.

---

## Controlled Values

To prevent invalid data entry, enums are used for:

- ComplaintCategory
- ComplaintPriority
- ComplaintStatus

Benefits:

- Restricts values to approved options
- Improves type safety
- Prevents spelling inconsistencies

---

## Status Lifecycle

Supported workflow:

NEW
→ UNDER_REVIEW
→ INVESTIGATING
→ RESOLVED
→ CLOSED

Alternative path:

NEW
→ REJECTED

UNDER_REVIEW
→ REJECTED

INVESTIGATING
→ REJECTED

CLOSED and REJECTED are terminal states.

---

## Status History

Each status change creates a
ComplaintStatusEvent.

This provides:

- Auditability
- Traceability
- Business history

---

## Design Decisions

### Dataclasses

Dataclasses were chosen because they provide:

- Clear model definitions
- Automatic constructors
- Better readability

### Enums

Enums enforce controlled values and satisfy
the requirement for validated domain states.

### Explicit Transition Rules

VALID_TRANSITIONS makes allowed status changes
easy to test and maintain.

---

## Definition of Done Checklist

- [x] Typed domain models
- [x] Controlled values enforced
- [x] Explicit status transitions
- [x] Invalid transitions tested
- [x] No SQL logic
- [x] No FastAPI logic