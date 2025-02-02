import boto3
from botocore.exceptions import ClientError
import os
import sys
from requests.utils import quote
from s3.file_name_base64 import encode


s3_resource = boto3.resource("s3")
s3_client = boto3.client("s3")


def upload_object_to_s3_bucket(
    local_fp: str, bucket_name: str, filename_encoding: bool
) -> str:
    """
    :param
        local_fp: local file path of an image
    :returns
        s3 url with encoded string
    """
    s3_key = __make_s3_key(local_fp, filename_encoding=filename_encoding)
    try:
        with open(local_fp, "rb") as f:
            s3_client.upload_fileobj(
                f, bucket_name, s3_key, ExtraArgs={"ContentType": "image/jpg"}
            )
            print(f"File {local_fp} uploaded to {bucket_name}/{s3_key}")
    except ClientError as e:
        print(f"Error uploading file to S3: {e}")

    # check if it's public
    s3_resource.Object(bucket_name, s3_key).wait_until_exists()
    s3_url = __get_s3_url(s3_key, bucket_name)
    return s3_key, s3_url


def __make_s3_key(local_fp: str, filename_encoding: bool):
    """
    encode by base64 but keep the filename extension like png or jpg
    """
    base_path, file_extension = os.path.splitext(local_fp)
    file_name = base_path.split("/")[-1]
    if filename_encoding:
        file_name = encode(file_name)
    return f"{file_name}{file_extension}"


def __get_s3_url(s3_key, bucket_name):
    return f"https://{bucket_name}.s3.amazonaws.com/{quote(s3_key)}"


def get_all_object_keys(bucket_name: str, return_format: str = "List[Dict]") -> list:
    res = s3_client.list_objects_v2(Bucket=bucket_name)
    is_truncated: bool = res["IsTruncated"]
    if is_truncated:
        print("truncated")

    keys = []
    if res["KeyCount"] != 0:
        if return_format == "List[Dict]":
            for content_dict in res["Contents"]:
                keys.append({"Key": content_dict["Key"]})
        elif return_format == "list":
            for content_dict in res["Contents"]:
                keys.append(content_dict["Key"])
        else:
            raise NotImplementedError("change your return format")

    return keys


def delete_all_s3_objects_in_bucket(bucket_name) -> None:
    confirmation = input(
        f"BEWARE! This operation will delete all the objects in your bucket {bucket_name}. Proceed? "
    )
    if confirmation != "yes":
        sys.exit(1)

    keys = get_all_object_keys(return_format="List[Dict]")
    delete_arg = {"Objects": keys, "Quiet": False}
    _ = s3_client.delete_objects(Bucket=bucket_name, Delete=delete_arg)
