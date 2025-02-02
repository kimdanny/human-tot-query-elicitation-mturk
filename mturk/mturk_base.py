import sys
import boto3
from typing import List, Dict
from datetime import datetime
import time


class MTurkBase:
    """
    All the utility functions are defined in MTurkBase class
    """

    def __init__(self, stage: str) -> None:
        environments = {
            "live": {
                "endpoint": "https://mturk-requester.us-east-1.amazonaws.com",
                "preview": "https://www.mturk.com/mturk/preview",
                "manage": "https://requester.mturk.com/mturk/manageHITs",
            },
            "sandbox": {
                "endpoint": "https://mturk-requester-sandbox.us-east-1.amazonaws.com",
                "preview": "https://workersandbox.mturk.com/mturk/preview",
                "manage": "https://requestersandbox.mturk.com/mturk/manageHITs",
            },
        }
        # Error Handling
        if stage is None:
            print("Pass your stage name: live or sandbox")
            sys.exit(1)

        if stage not in {"live", "sandbox"}:
            print("Stage name should be either live or sandbox")
            sys.exit(1)

        # set mturk env
        self.stage = stage
        self.mturk_env = environments[self.stage]
        self.mturk_client = boto3.client(
            service_name="mturk",
            region_name="us-east-1",
            endpoint_url=self.mturk_env["endpoint"],
        )

        # Test that you can connect to the API by checking your account balance
        user_balance = self.mturk_client.get_account_balance()
        # In Sandbox this always returns $10,000. In live, it will be your acutal balance.
        print("Your account balance is {}".format(user_balance["AvailableBalance"]))

    def get_hit_status(self, hit_id: str) -> dict:
        response = self.mturk_client.get_hit(HITId=hit_id)
        status = {
            "status": response["HIT"]["HITStatus"],
            "CreationTime": response["HIT"]["CreationTime"],
            "NumberOfAssignmentsPending": response["HIT"]["NumberOfAssignmentsPending"],
            "NumberOfAssignmentsAvailable": response["HIT"][
                "NumberOfAssignmentsAvailable"
            ],
            "NumberOfAssignmentsCompleted": response["HIT"][
                "NumberOfAssignmentsCompleted"
            ],
        }
        return status

    def get_all_hits(self) -> list:
        """
        Returns a list of information of each HIT
        """
        response = self.mturk_client.list_hits(MaxResults=100)
        return response["HITs"]

    def get_all_hit_ids(self) -> list:
        hit_ids = []
        response = self.mturk_client.list_hits(MaxResults=100)
        for hit_dict in response["HITs"]:
            hit_ids.append(hit_dict["HITId"])
        return hit_ids

    def get_reviewable_hits(self) -> List[Dict]:
        response = self.mturk_client.list_reviewable_hits(
            Status="Reviewable", MaxResults=100
        )
        return response["HITs"]

    def get_reviewing_hits(self):
        response = self.mturk_client.list_reviewable_hits(
            Status="Reviewing", MaxResults=100
        )
        return response["HITs"]

    def delte_hit(self, hit_id: str):
        """
        sample response:
        {'ResponseMetadata':
            {'RequestId': '5ca563e5-8634-434b-a0c7-288c5b201d59',
            'HTTPStatusCode': 200,
            'HTTPHeaders':
                {'x-amzn-requestid': '5ca563e5-8634-434b-a0c7-288c5b201d59',
                'content-type': 'application/x-amz-json-1.1',
                'content-length': '2',
                'date': 'Tue, 12 Dec 2023 02:38:50 GMT'
                },
            'RetryAttempts': 0}
        }
        """
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mturk/client/delete_hit.html
        res = self.mturk_client.delete_hit(HITId=hit_id)
        return res

    def expire_hit(self, hit_id: str):
        res = self.mturk_client.update_expiration_for_hit(
            HITId=hit_id, ExpireAt=datetime(2015, 1, 1)
        )
        return res

    def _delete_all_hits(self) -> list:
        """
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mturk/client/delete_hit.html
        Dangerous operation.
        Deleting all deletable HITs created. Also expire all HITs.
        Deletable means:
        You can only dispose of HITs that are in the Reviewable state,
            with all of their submitted assignments already either approved or rejected.
        If you call the DeleteHIT operation on a HIT that is not in the Reviewable state
            (for example, that has not expired, or still has active assignments),
            or on a HIT that is Reviewable but without all of its submitted assignments already approved or rejected,
            the service will return an error.
        Returns: delted HIT IDs.
        """
        if self.stage == "live":
            raise NotImplementedError(
                "Does not support deleting all HITs in live stage"
            )

        confirmation = input(
            "BEWARE! This operation will expire and delete all the HITs in your sandbox stage. Proceed? "
        )
        if confirmation != "yes":
            sys.exit(1)
        print("Remember to delete the aws table entries manually")

        hits = self.get_all_hits()
        deleted_hit_ids = []
        for hit_dict in hits:
            hit_id = hit_dict["HITId"]
            _ = self.expire_hit(hit_id)
            print(f"HIT ID {hit_id} is just expired")
            try:
                _ = self.delte_hit(hit_id=hit_id)
                deleted_hit_ids.append(hit_id)
            except self.mturk_client.exceptions.RequestError as e:
                print(
                    f"HIT ID {hit_id} could not be deleted so try accepting all assignments"
                )
                response = self.mturk_client.list_assignments_for_hit(
                    HITId=hit_id,
                    AssignmentStatuses=["Submitted"],
                    MaxResults=10,  # since the max assignments per HIT is set to 10 in creation
                )
                assignments = response["Assignments"]
                for assignment in assignments:
                    assignment_id = assignment["AssignmentId"]
                    self.mturk_client.approve_assignment(
                        AssignmentId=assignment_id,
                        RequesterFeedback="Thank you for your participation.",
                        OverrideRejection=False,
                    )
                    print(f"Assignment {assignment_id} is approved.")
                time.sleep(1)
                _ = self.delte_hit(hit_id=hit_id)
                deleted_hit_ids.append(hit_id)
                print(f"HIT ID {hit_id} is now deleted")

        return deleted_hit_ids
