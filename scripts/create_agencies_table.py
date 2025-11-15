#!/usr/bin/env python3
"""
Create DynamoDB table for agencies
"""
import os
import boto3

AWS_REGION = os.getenv('AWS_REGION', 'ap-southeast-2')
TABLE_NAME = os.getenv('AGENCIES_TABLE_NAME', 'agencies')

def create_agencies_table():
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    
    table = dynamodb.create_table(
        TableName=TABLE_NAME,
        KeySchema=[
            {'AttributeName': 'agency_id', 'KeyType': 'HASH'},
        ],
        AttributeDefinitions=[
            {'AttributeName': 'agency_id', 'AttributeType': 'S'},
            {'AttributeName': 'keyword', 'AttributeType': 'S'},
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'keyword-index',
                'KeySchema': [
                    {'AttributeName': 'keyword', 'KeyType': 'HASH'},
                ],
                'Projection': {'ProjectionType': 'ALL'},
            }
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    
    table.wait_until_exists()
    print(f"✅ Table created: {table.table_name}")
    return table

if __name__ == '__main__':
    create_agencies_table()
