#!/usr/bin/env python3
"""
Simple AWS Resource Cleanup Script
Delete AWS resources for serverless applications easily.
"""

import boto3
import sys

# ============================================================================
# CONFIGURATION - Edit these values for your setup
# ============================================================================
ENVIRONMENT = 'staging'  # Change to 'prod' for production
REGION = 'us-east-1'     # Change to your AWS region

# Resource names (automatically built from environment)
RESOURCES = {
    'lambda': f"{ENVIRONMENT}-health-check-function",
    'role': f"{ENVIRONMENT}-health-check-function-role",
    'table': f"{ENVIRONMENT}-requests-db",
    'logs': f"/aws/lambda/{ENVIRONMENT}-health-check-function"
}

# ============================================================================
# MAIN CLEANUP LOGIC
# ============================================================================

def cleanup():
    """Delete all AWS resources."""
    
    # Setup AWS clients
    clients = {
        'lambda': boto3.client('lambda', region_name=REGION),
        'iam': boto3.client('iam'),
        'dynamodb': boto3.client('dynamodb', region_name=REGION),
        'logs': boto3.client('logs', region_name=REGION)
    }
    
    print(f"\n🗑️  Cleaning up {ENVIRONMENT} environment...\n")
    
    # 1. Delete Lambda function
    try:
        clients['lambda'].delete_function(FunctionName=RESOURCES['lambda'])
        print(f"✓ Deleted Lambda: {RESOURCES['lambda']}")
    except:
        print(f"⊘ Lambda not found: {RESOURCES['lambda']}")
    
    # 2. Delete CloudWatch logs
    try:
        clients['logs'].delete_log_group(logGroupName=RESOURCES['logs'])
        print(f"✓ Deleted Logs: {RESOURCES['logs']}")
    except:
        print(f"⊘ Logs not found: {RESOURCES['logs']}")
    
    # 3. Detach and delete IAM role
    try:
        # Detach managed policies
        policies = clients['iam'].list_attached_role_policies(RoleName=RESOURCES['role'])
        for policy in policies.get('AttachedPolicies', []):
            clients['iam'].detach_role_policy(
                RoleName=RESOURCES['role'],
                PolicyArn=policy['PolicyArn']
            )
        
        # Delete inline policies
        inline = clients['iam'].list_role_policies(RoleName=RESOURCES['role'])
        for policy_name in inline.get('PolicyNames', []):
            clients['iam'].delete_role_policy(
                RoleName=RESOURCES['role'],
                PolicyName=policy_name
            )
        
        # Delete role
        clients['iam'].delete_role(RoleName=RESOURCES['role'])
        print(f"✓ Deleted IAM Role: {RESOURCES['role']}")
    except:
        print(f"⊘ IAM Role not found: {RESOURCES['role']}")
    
    # 4. Delete DynamoDB table
    try:
        clients['dynamodb'].delete_table(TableName=RESOURCES['table'])
        print(f"✓ Deleted DynamoDB: {RESOURCES['table']}")
    except:
        print(f"⊘ DynamoDB not found: {RESOURCES['table']}")
    
    print("\n✅ Cleanup complete!\n")


# ============================================================================
# RUN THE SCRIPT
# ============================================================================

if __name__ == "__main__":
    print("\n⚠️  WARNING: This will DELETE AWS resources!")
    print(f"   Environment: {ENVIRONMENT}")
    print(f"   Region: {REGION}\n")
    
    confirm = input("Type 'yes' to continue: ").strip().lower()
    
    if confirm == 'yes':
        cleanup()
    else:
        print("\n❌ Cancelled. Nothing was deleted.\n")
        sys.exit(0)
