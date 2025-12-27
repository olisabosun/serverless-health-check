import json
import boto3
import os
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table_name = os.environ['DYNAMODB_TABLE']
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    # Log the incoming request
    print(f"Received event: {json.dumps(event)}")
    
    # Generate unique ID
    request_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    # Prepare item for DynamoDB
    item = {
        'id': request_id,
        'timestamp': timestamp,
        'method': event.get('httpMethod', 'UNKNOWN'),
        'path': event.get('path', '/health'),
        'source_ip': event.get('requestContext', {}).get('identity', {}).get('sourceIp', 'unknown')
    }
    
    # Save to DynamoDB
    try:
        table.put_item(Item=item)
        print(f"Successfully saved request {request_id} to DynamoDB")
    except Exception as e:
        print(f"Error saving to DynamoDB: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'error',
                'message': 'Failed to save request'
            })
        }
    
    # Return success response
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'status': 'healthy',
            'message': 'Request processed and saved.',
            'request_id': request_id
        })
    }
