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


class CreateHIT(MTurkBase):
    def __init__(self, stage: str, worker_requirements=None) -> None:
        # instances defined from super:
        # stage, mturk_env, client
        super().__init__(stage=stage)
        if worker_requirements is None:
            self.worker_requirements = [
                {
                    "QualificationTypeId": "000000000000000000L0",
                    "Comparator": "GreaterThanOrEqualTo",
                    "IntegerValues": [80],
                    "RequiredToPreview": True,
                }
            ]
        else:
            self.worker_requirements = worker_requirements

    def create(self, front_end_xml_fp: str, hit_config: dict):
        # Create the HIT
        # https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_CreateHITOperation.html
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mturk/client/create_hit.html
        response = self.mturk_client.create_hit(
            MaxAssignments=10,  # The number of times the HIT can be accepted and completed before the HIT becomes unavailable.
            LifetimeInSeconds=7890000,  # 3 months in seconds
            AssignmentDurationInSeconds=600,  # 10 minutes in seconds
            Title=hit_config["title"],
            Keywords=hit_config["keywords"],
            Description=hit_config["description"],
            Reward=hit_config["reward"],
            Question=open(front_end_xml_fp, "r").read(),
            QualificationRequirements=self.worker_requirements,
        )
        return response
