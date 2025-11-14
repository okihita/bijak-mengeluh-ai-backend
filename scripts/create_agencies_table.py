#!/usr/bin/env python3
"""
Create DynamoDB table for agencies
"""
import boto3

def create_agencies_table():
    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
    
    table = dynamodb.create_table(
        TableName='agencies',
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
                'BillingMode': 'PAY_PER_REQUEST'
            }
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    
    table.wait_until_exists()
    print(f"✅ Table created: {table.table_name}")
    return table

if __name__ == '__main__':
    create_agencies_table()
