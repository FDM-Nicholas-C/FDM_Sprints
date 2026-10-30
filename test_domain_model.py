import pytest

from models import (
    Complaint,
    ComplaintCategory,
    ComplaintPriority,
    ComplaintStatus
)


def create_complaint():

    return Complaint(
        complaint_id="CMP001",
        customer_id="CUS001",
        category=ComplaintCategory.FEES,
        priority=ComplaintPriority.HIGH,
        description="Unexpected charge"
    )


def test_default_status():
    complaint = create_complaint()

    assert complaint.status == ComplaintStatus.NEW


def test_valid_transition():

    complaint = create_complaint()

    complaint.change_status(
        ComplaintStatus.UNDER_REVIEW
    )

    assert complaint.status == ComplaintStatus.UNDER_REVIEW


def test_valid_transition_chain():

    complaint = create_complaint()

    complaint.change_status(
        ComplaintStatus.UNDER_REVIEW
    )

    complaint.change_status(
        ComplaintStatus.INVESTIGATING
    )

    complaint.change_status(
        ComplaintStatus.RESOLVED
    )

    assert complaint.status == ComplaintStatus.RESOLVED


def test_invalid_transition():

    complaint = create_complaint()

    with pytest.raises(ValueError):

        complaint.change_status(
            ComplaintStatus.CLOSED
        )


def test_history_is_recorded():

    complaint = create_complaint()

    complaint.change_status(
        ComplaintStatus.UNDER_REVIEW
    )

    assert len(complaint.history) == 1


def test_rejected_is_terminal():

    complaint = create_complaint()

    complaint.change_status(
        ComplaintStatus.REJECTED
    )

    with pytest.raises(ValueError):

        complaint.change_status(
            ComplaintStatus.UNDER_REVIEW
        )