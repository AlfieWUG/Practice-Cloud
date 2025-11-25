#!/usr/bin/env python3
"""Create DynamoDB tables for Quick Assess using boto3."""
import boto3
import sys
import os

endpoint = os.getenv("DYNAMODB_ENDPOINT", "http://localhost:8001")

dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url=endpoint,
    aws_access_key_id="test",
    aws_secret_access_key="test",
    region_name="us-east-1",
)

client = dynamodb.meta.client

tables = [
    {
        "name": "agentic-services-quick-assess",
        "key": "assessment_id",
    },
    {
        "name": "agentic-services-quick-assess-errors",
        "key": "assessment_id",
    },
]

for table_config in tables:
    try:
        client.create_table(
            TableName=table_config["name"],
            AttributeDefinitions=[
                {"AttributeName": table_config["key"], "AttributeType": "S"}
            ],
            KeySchema=[{"AttributeName": table_config["key"], "KeyType": "HASH"}],
            BillingMode="PAY_PER_REQUEST",
        )
        print(f"✅ Created table: {table_config['name']}")
    except client.exceptions.ResourceInUseException:
        print(f"⚠️  Table already exists: {table_config['name']}")
    except Exception as e:
        print(f"❌ Error creating {table_config['name']}: {e}")
        sys.exit(1)

print("\n✅ All tables ready!")





