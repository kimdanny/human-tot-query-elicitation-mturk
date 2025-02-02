# End to End pipeline from retrieving HITs from MTurk to logging to DynamoDB
import sys
import json
from xml.dom.minidom import parseString
from mturk.retrieve_hit import RetrieveHIT
from dynamo_db.dynamo_db_handler import DynamoDBHandler
from typing import List, Dict


def main():
    # Remind the forgetful.
    if len(sys.argv) != 2:
        print("Usage: python e2e_retrieve.py <STAGE>")
        sys.exit(1)

    STAGE = sys.argv[1]

    if STAGE == "live":
        HIT_TABLE_NAME = "HIT-Table"
        ASS_TABLE_NAME = "Assignment-Table"
    elif STAGE == "sandbox":
        HIT_TABLE_NAME = f"HIT-Table-{STAGE}"
        ASS_TABLE_NAME = f"Assignment-Table-{STAGE}"
    else:
        raise NotImplementedError(f"Stage {STAGE} is not supported.")

    # mturk and dynamo handlers
    mturk_client = RetrieveHIT(stage=STAGE)
    hit_table_handler = DynamoDBHandler(
        table_name=HIT_TABLE_NAME, partition_key="HITID"
    )
    ass_table_handler = DynamoDBHandler(
        table_name=ASS_TABLE_NAME, partition_key="AssignmentID", sort_key="HITID"
    )

    # 1. get HITs to be checked from HIT-Table
    partiql_statement = (
        f'SELECT HITID FROM "{HIT_TABLE_NAME}" WHERE AllAssignmentsDone=?'
    )
    res: List[Dict] = hit_table_handler.run_partiql_statment(
        partiql_statement, parameters=[0]
    )
    hit_ids = [hit_info["HITID"] for hit_info in res]
    del res

    if len(hit_ids) == 0:
        print("No HITs to review")

    # 2. for each HIT, get submitted assignments list
    for hit_id in hit_ids:
        print(f"Looking into HIT {hit_id}")
        assignments = mturk_client.get_submitted_assignments_for_hit(hit_id=hit_id)
        print(f"{len(assignments)} assignments were submitted in HIT {hit_id}")

        # 3. for each submitted assignment in HIT, get info, validate, log, and approve/reject
        for assignment in assignments:
            # info to log
            worker_id_to_log = assignment["WorkerId"]
            assignment_id_to_log = assignment["AssignmentId"]
            assert hit_id == assignment["HITId"]
            tot_image_id_to_log = "N/A"
            phase_1_to_log = "N/A"
            phase_2_to_log = "N/A"
            phase_3_to_log = "N/A"
            phase_4_to_log = "N/A"
            time_stamps_to_log = "N/A"
            turn_took_to_tot = "N/A"
            # this contains logs that happened before reaching a ToT stage
            pre_tot_log_to_log = dict()  # ordered dict (must use python > 3.6)

            # parsing answer with xml and json
            answer_xml = parseString(assignment["Answer"])
            answer = answer_xml.getElementsByTagName("FreeText")[0]
            answer = answer.childNodes[0].nodeValue[1:-1]
            data_dict = json.loads(answer)
            del answer_xml, answer

            try:
                data_dict = json.loads(data_dict["mturk_data"])
                user_responses: dict = data_dict["userResponses"]
                time_stamps_to_log = str(data_dict["timestamps"])
                del data_dict
                cnt = 0
                for image, phase_logs in user_responses.items():
                    if "Phase_3_(ToT_query)" in phase_logs:
                        # Should be the last entry of the user_responses.items()
                        tot_image_id_to_log = image
                        phase_1_to_log = phase_logs["Phase_1_(recognize)"]
                        phase_2_to_log = phase_logs["Phase_2_(object_name)"]
                        phase_3_to_log = phase_logs["Phase_3_(ToT_query)"]
                        phase_4_to_log = phase_logs["Phase_4_(confirm)"]
                        turn_took_to_tot = str(cnt)
                    else:
                        # not a tot state so saving to pre_tot_log_to_log
                        pre_tot_log_to_log.update({image: phase_logs})
                        cnt += 1

            except KeyError:
                # No "mturk_data" in data_dict, meaning that
                # the worker skipped all images by pressing No's in phase 1
                # N/A's will be logged into all the attributes of the assignment table,
                # so suppressing the error
                pass

            # 3-1. update Assignment-Table with turker's answer
            payload = {
                "AssignmentID": {"S": assignment_id_to_log},
                "HITID": {"S": hit_id},
                "WorkerID": {"S": worker_id_to_log},
                "ToTImage": {"S": tot_image_id_to_log},
                "Phase1": {"S": phase_1_to_log},
                "Phase2": {"S": phase_2_to_log},
                "Phase3": {"S": phase_3_to_log},
                "Phase4": {"S": phase_4_to_log},
                "TimeStamps": {"S": time_stamps_to_log},
                "TurnTookToToT": {"S": turn_took_to_tot},
                "PreToTLog": {"S": str(pre_tot_log_to_log)},
            }
            res = ass_table_handler.put_item(payload=payload)
            if res["ResponseMetadata"]["HTTPStatusCode"] == 200:
                print(
                    f"Successfully stored Assignment {assignment_id_to_log} info into table: {ASS_TABLE_NAME}"
                )
            else:
                raise Exception("DB storing has failed")

            # 3-2. update AssignmentsID and possibly AllAssignmentsDone in HIT-Table
            # curr_ass_ids -> [{'AssignmentID': ['placeholder', 'xxx']}]
            curr_ass_ids: List[Dict] = hit_table_handler.run_partiql_statment(
                statement=f'SELECT AssignmentID FROM "{HIT_TABLE_NAME}" WHERE HITID=?',
                parameters=[hit_id],
            )
            curr_ass_ids = curr_ass_ids[0]["AssignmentID"]
            curr_ass_ids.append(assignment_id_to_log)
            new_ass_ids = list(set(curr_ass_ids))
            del curr_ass_ids
            new_ass_ids = [
                {"S": ass_id} for ass_id in new_ass_ids if ass_id != "placeholder"
            ]

            # update payload and rules depending on the length of assignments filled
            # remember: max assignments per HIT were set to 10 in creation.
            if len(new_ass_ids) < 10:
                key_info = {"HITID": {"S": hit_id}}
                update_expression = "SET AssignmentID = :a"
                expression_att_vals = {":a": {"L": new_ass_ids}}
                return_values = "UPDATED_NEW"
            else:
                key_info = {"HITID": {"S": hit_id}}
                update_expression = "SET AssignmentID = :a, AllAssignmentsDone = :b"
                expression_att_vals = {":a": {"L": new_ass_ids}, ":b": {"N": 1}}
                return_values = "UPDATED_NEW"

            # update HIT-Table with the rules
            _ = hit_table_handler.update_item(
                key_info=key_info,
                update_expression=update_expression,
                expression_att_vals=expression_att_vals,
                return_values=return_values,
            )

            # 3-3. approve/reject. Now just automatic approval
            mturk_client.approve_assignment(assignment_id=assignment_id_to_log)


if __name__ == "__main__":
    main()
