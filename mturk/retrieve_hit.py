# Copyright 2017 Amazon.com, Inc. or its affiliates

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import boto3
from typing import List, Dict
from mturk.mturk_base import MTurkBase

# Before connecting to MTurk, set up your AWS account and IAM settings as
# described here:
# https://blog.mturk.com/how-to-use-iam-to-control-api-access-to-your-mturk-account-76fe2c2e66e2
#
# Follow AWS best practices for setting up credentials here:
# http://boto3.readthedocs.io/en/latest/guide/configuration.html

# Use the Amazon Mechanical Turk Sandbox to publish test Human Intelligence
# Tasks (HITs) without paying any money.  Sign up for a Sandbox account at
# https://requestersandbox.mturk.com/ with the same credentials as your main
# MTurk account.


class RetrieveHIT(MTurkBase):
    def __init__(self, stage: str) -> None:
        # instances defined from super:
        # stage, mturk_env, client
        super().__init__(stage=stage)

    def get_submitted_assignments_for_hit(self, hit_id: str) -> List[Dict]:
        response = self.mturk_client.list_assignments_for_hit(
            HITId=hit_id,
            AssignmentStatuses=["Submitted"],
            MaxResults=10,  # since the max assignments per HIT is set to 10 in creation
        )
        return response["Assignments"]

    def get_approved_assignments_for_hit(self, hit_id: str) -> List[Dict]:
        response = self.mturk_client.list_assignments_for_hit(
            HITId=hit_id,
            AssignmentStatuses=["Approved"],
            MaxResults=10,  # since the max assignments per HIT is set to 10 in creation
        )
        return response["Assignments"]

    def get_rejected_assignments_for_hit(self, hit_id: str) -> List[Dict]:
        response = self.mturk_client.list_assignments_for_hit(
            HITId=hit_id,
            AssignmentStatuses=["Rejected"],
            MaxResults=10,  # since the max assignments per HIT is set to 10 in creation
        )
        return response["Assignments"]

    def approve_assignment(self, assignment_id: str) -> None:
        """
        Can only approve assignment of AssignmentStatus=="Submitted"
        """
        self.mturk_client.approve_assignment(
            AssignmentId=assignment_id,
            RequesterFeedback="Thank you for your participation.",
            OverrideRejection=False,
        )
        print(f"Assignment {assignment_id} is approved.")

    def create_put_request_json_for_db_batch_write(self):
        """
        Creates PutRequest JSON for DynamoDB's batch write
        Example format can be found:
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/batch_write_item.html
        """
        pass
