import boto3
from datetime import datetime, timedelta, timezone
from botocore.exceptions import ClientError


def lambda_handler(event, context):

    DRY_RUN = (event or {}).get("dry_run", True)

    client = boto3.client("ec2")

    # Getting all instance IDs and all volume IDs attached to the instances

    ec2_response = client.describe_instances()

    instance_volumes = set()

    for reservation in ec2_response["Reservations"]:
        for instance in reservation["Instances"]:
            for mappings in instance["BlockDeviceMappings"]:
                if "Ebs" in mappings:
                    instance_volumes.add(mappings["Ebs"]["VolumeId"])

    print(f"Attached volumes: {len(instance_volumes)}")

    # Getting all Volume IDs

    vol_response = client.describe_volumes()

    volume_ids = set()

    for volume in vol_response["Volumes"]:
        volume_ids.add(volume["VolumeId"])

    print(f"Total volumes: {len(volume_ids)}")

    # comparing all volumes with attached volumes to get all IDs of unattached volumes

    unattached_volumes = volume_ids.difference(instance_volumes)

    print(f"Unattached volumes: {len(unattached_volumes)}")

    # Snapshots. Getting their IDs, volumes attached, and their start times. Saving to a list of dictionaries this time

    snapshot_response = client.describe_snapshots(OwnerIds=["self"])

    checked = 0
    candidates = 0
    deleted = 0

    snapshots = snapshot_response["Snapshots"]
    print(f"Total snapshots: {len(snapshots)}")

    threshold_date = datetime.now(timezone.utc) - timedelta(days=30)

    for snapshot in snapshots:

        checked += 1

        snapshot_id = snapshot["SnapshotId"]
        volume_id = snapshot.get("VolumeId")
        start_time = snapshot["StartTime"]

        if volume_id is None:
            print(f"Skipping {snapshot_id}: no VolumeId")
            continue

        # Deleting snapshots that are not within the list of all volume_ids. And snapshots whose volumes are unattached and are older than 30 days

        reason = None

        if volume_id not in volume_ids:
            reason = "missing volume"

        elif volume_id in unattached_volumes and start_time < threshold_date:
            reason = "unattached volume older than 30 days"

        if reason:

            candidates += 1

            if DRY_RUN:
                print(
                    f'Would delete: {snapshot_id} | reason: {reason}'
                )
            else:
                print("Deleting:", snapshot_id)
                try:
                    client.delete_snapshot(SnapshotId=snapshot_id)
                    deleted += 1
                except ClientError as e:
                    print(
                        f"Failed to delete {snapshot_id}: {e.response['Error']['Code']} : {e.response['Error']['Message']}"
                    )

    print("----- SUMMARY -----")
    print(f"Snapshots checked: {checked}")
    print(f"Candidates found: {candidates}")
    print(f"Deleted: {deleted}")
    print(f"Dry run: {DRY_RUN}")


# Developed an AWS Lambda cost-optimization function in Python using boto3 to identify orphaned EBS snapshots, implement dry-run validation, and safely delete outdated resources with exception handling and execution logging.
