# AWS EBS Snapshot Cleanup (Lambda + boto3)

## Overview

This project is a simple AWS Lambda function written in Python using boto3.
It helps reduce AWS costs by finding and cleaning up unused (or orphaned) EBS snapshots.

The function supports a **dry-run mode**, so you can safely review what will be deleted before actually doing it.

---

## What it does

The function:

* collects all EC2 instances and their attached volumes
* gets all EBS volumes
* finds unattached volumes
* checks all snapshots owned by the account
* applies cleanup rules

### Snapshots are deleted if:

* the source volume no longer exists
* OR the volume is unattached **and** the snapshot is older than 30 days

---

## How to use

### Dry run (default)

```json
{ "dry_run": true }
```

Only prints what would be deleted.

### Actual deletion

```json
{ "dry_run": false }
```

Deletes matching snapshots.

---

## Deployment

* Create a Lambda function (Python 3.x)
* Paste the script
* Attach an IAM role with permissions:

  * `ec2:DescribeInstances`
  * `ec2:DescribeVolumes`
  * `ec2:DescribeSnapshots`
  * `ec2:DeleteSnapshot`

---

## Test scenarios

I tested the function using:

1. **Snapshot of attached volume**
   → should NOT be deleted

2. **Snapshot of unattached volume**
   → deleted only if older than threshold

3. **Snapshot of deleted volume**
   → should be deleted

4. **Snapshot without VolumeId (edge case)**
   → skipped

---

## Example output

```
Attached volumes: 2
Total volumes: 4
Unattached volumes: 2
Total snapshots: 6

Would delete: snap-123 | reason: missing
Would delete: snap-456 | reason: unattached & old

----- SUMMARY -----
Snapshots checked: 6
Candidates found: 2
Deleted: 0
Dry run: True
```

---

## Notes / possible improvements

* add pagination for large environments
* add tagging-based approval
* export results (S3, etc.)

---

## Tech used

* Python
* AWS Lambda
* boto3


<img width="1918" height="888" alt="Screenshot from 2026-03-18 11-52-22" src="https://github.com/user-attachments/assets/81802d25-cbee-47a2-9b5f-912a810045e6" />

<img width="1918" height="888" alt="Screenshot from 2026-03-18 12-02-28" src="https://github.com/user-attachments/assets/55fc4bcc-bbdc-461e-bd24-b8db71549eef" />

