from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import List


class ComplaintCategory(Enum):
    SERVICE = "Service"
    FEES = "Fees"
    FRAUD = "Fraud"
    ACCOUNT = "Account"
    OTHER = "Other"


class ComplaintPriority(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class ComplaintStatus(Enum):
    NEW = "New"
    UNDER_REVIEW = "Under Review"
    INVESTIGATING = "Investigating"
    RESOLVED = "Resolved"
    CLOSED = "Closed"
    REJECTED = "Rejected"


VALID_TRANSITIONS = {
    ComplaintStatus.NEW: [
        ComplaintStatus.UNDER_REVIEW,
        ComplaintStatus.REJECTED
    ],
    ComplaintStatus.UNDER_REVIEW: [
        ComplaintStatus.INVESTIGATING,
        ComplaintStatus.REJECTED
    ],
    ComplaintStatus.INVESTIGATING: [
        ComplaintStatus.RESOLVED,
        ComplaintStatus.REJECTED
    ],
    ComplaintStatus.RESOLVED: [
        ComplaintStatus.CLOSED
    ],
    ComplaintStatus.CLOSED: [],
    ComplaintStatus.REJECTED: []
}


@dataclass
class Customer:
    customer_id: str
    first_name: str
    last_name: str
    email: str


@dataclass
class Account:
    account_id: str
    customer_id: str
    account_type: str
    balance: float


@dataclass
class ComplaintStatusEvent:
    previous_status: ComplaintStatus
    new_status: ComplaintStatus
    changed_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Complaint:
    complaint_id: str
    customer_id: str
    category: ComplaintCategory
    priority: ComplaintPriority
    description: str
    status: ComplaintStatus = ComplaintStatus.NEW
    history: List[ComplaintStatusEvent] = field(default_factory=list)

    def change_status(self, new_status: ComplaintStatus):

        if new_status not in VALID_TRANSITIONS[self.status]:
            raise ValueError(
                f"Invalid transition from "
                f"{self.status.value} "
                f"to "
                f"{new_status.value}"
            )

        event = ComplaintStatusEvent(
            previous_status=self.status,
            new_status=new_status
        )

        self.history.append(event)
        self.status = new_status
