**Overview:**

- The Banking Complaint Resolution Assistant is for the Complaint Analyst to understand the complaint, verfiy the customer's history, locate the applicable policy and prepare a recommendation.

- Complaint analysts, customers, and supervisors will be the only ones interacting with the tool.

- This makes information handling faster and supports the professional judgements of complaint analysts in handling complaints.

**Scope**

- What is included:

  - Get complaint

  - Parse complaint

  - View customer

  - View Account

  - View complaint

  - Get customer account history

  - Search Policy

  - Cite Policy

  - Create Review Request

  - Update case status

  - Triage case

  - Identify missing information

  - Draft Customer Response

  - Record Audit event

  - Propose next action

  - Pause for human review

**Non-goals**

- What is excluded:

• Using real customer or production banking data.

• Automatically making final legal, regulatory, fraud, credit or compensation decisions.

• Giving the model unrestricted database or system access.

• Treating generated text as policy evidence without a valid source citation.

• Building every possible banking complaint process or product integration.

**Actors**

- Complaint Analyst

  - Review intake

  - Investigate evidence

  - Prepare recommendation

  - Communicate outcome

  - Escalate

  - Condition: Can view emails and System summaries, can send cases to Supervisors

- Supervisor/Reviewer

  - Review escalated/sensitive cases and approve/reject proposed action

  - Condition: Only views escalated/sensitive cases

- System

  - Parses complaint emails, gathers customer information, search/cite policy, triage, proposes actions for review

  - Condition: can only parse and view emails, cannot take actions

**Preconditions**

- The customer has an account with the bank.

- The customer issued a complaint via email, phone, branch, and web channels.

**Core Flows**

- The expected behavior:

1. The complaint has been received.

2. Does the complaint have the required data?

   1. If No, then request missing information/manual triage.

   2. If Yes Move to Step 3.

3. Does the complaint report an immediate safety, active account takeover, repeated unauthorized activity or inability to secure?

   3. If yes move to Step 7

   4. If No move to Step 4

4. Is the amount >= CAD $2,500 OR amount >= CAD $1,000 plus an unauthorized indicator?

   5. If yes move to Step 8

   6. If no move to Step 5

5. Is the amount CAD $500-$2,4999.99?

   7. If yes move to Step 9

   8. If no move to Step 6

6. Complaint enters Standard Queue. Move to Step 10.

7. Complaint enters Critical Queue (Immediate fraud/security and human review) Move to Step 10.

8. Complaint enters High Queue (Expedited analyst queue) Move to Step 10.

9. Complaint enters Medium Queue (Prompt analyst queue) Move to Step 10.

10. Sort the Complaints from Critical/High/Medium/Standard.

11. Retrieve structured facts + approved procedure.

12. Prepare evidence package.

13. Human reviewer decision; Complaint Analyst handles things below Critical, Supervisor handles Critical.

14. Approved response, audit trail, and closure.

**Business** **Rules**

- Assistant summaries require a preexisting email

- A summary requires a complaint id, a customer id, a customer statement, a transaction, additional indicators, requested outcome, and related policy

**Error Conditions** **and Edge Cases**

- Edge cases

- Invalid inputs

- Conflicting states

- Forbidden actions

- Exact error codes or categories

- Invalid ‘complaintId’ format -> 400, field=”complaintId"

- Invalid ‘accountId’ format -> 400, field=”accountId”

- Missing or invalid ‘transaction’-> 400, field =”transactionId”

- Missing or invalid ‘fee’->400, field=”feeId”

- Missing or invalid ‘request’->400, field=”requestId”

- 

**NFRs**

- Audit logs exist for each customer's complaint.

- The latency is less than 1min for each complaint

- No sensitive information being disclosed to people uninvolved.

**High-Level Interface expectation**

- Intake: receive and record the complaint narrative and available identifiers

- Triage: classify the complaint, assess urgency, and identify missing information

- Investigation: retrieve structured history and relevant approved policy evidence.

- Recommendation: prepare a grounded summary and proposed next action.

- Review and approval: route sensitive or escalated cases to a responsible human reviewer.

- Response and closure: communicate the approved outcome and retain evidence, status and audit history. 

**Domain Rules:**

- All ids must be unique

- Severity is determined from the company policy

- Escalation is determined from company policy

- All possible information should appear in the summary to help Complaint Analysts make the best possible judgements

**Success Criteria:**

- Given 100 working complaints, the tool will be able to correctly parse the necessary information, perform triage, draft the customer response, and wait for human review 95 out of 100 times.

- Give a complaint with missing information, the tool will be able to determine what information is missing, throw an exception, and then leave the complaint for human review.

**Security Constraints:**

- Protected from SQL Injection attacks

- Assistant must forget customer data after each case summary

- Staff has to be authorized to view customer data

**Audit Constraints:**

- Records all staff involved in approvals and denials

- Records all staff handling a claim

- Records all time logs for claim arrivals and response departure

- Records severity and transfers to higher priority

- Records location information

**Reliability Constraints:**

- Model should be at least 95% accurate in parsing patient information

- Model should be at least 95% accurate in parsing claims policy

- Models should be at least 95% accurate in judging severity
