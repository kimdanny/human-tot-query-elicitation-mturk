import boto3
from boto3.dynamodb.conditions import Key
from typing import List, Dict


class DynamoDBHandler:
    """
    handler dedicated for one table set at instantiation
    Examples:
    https://docs.aws.amazon.com/code-library/latest/ug/python_3_dynamodb_code_examples.html
    """

    def __init__(self, table_name: str, partition_key: str, sort_key=None) -> None:
        self.client = boto3.client("dynamodb")
        self.resource = boto3.resource("dynamodb")
        self.TABLE = self.resource.Table(table_name)
        self.TABLE_NAME = table_name
        self.PARTITION_KEY = partition_key
        self.SORT_KEY = sort_key

    def batch_write_item(self):
        pass

    def put_item(self, payload: dict):
        response = self.client.put_item(TableName=self.TABLE_NAME, Item=payload)
        return response

    def update_item(
        self, key_info: dict, update_expression, expression_att_vals, return_values
    ):
        """
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/update_item.html
        """
        response = self.client.update_item(
            Key=key_info,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_att_vals,
            ReturnValues=return_values,
            TableName=self.TABLE_NAME,
        )
        return response["Attributes"]

    def query_table_pk(self, pk, value):
        """
        Only partition key is supported
        """
        response = self.TABLE.query(KeyConditionExpression=Key(pk).eq(value))
        return response["Items"]

    def run_partiql_statment(self, statement: str, parameters: list) -> List[Dict]:
        response = self.resource.meta.client.execute_statement(
            Statement=statement, Parameters=parameters
        )
        return response["Items"]
