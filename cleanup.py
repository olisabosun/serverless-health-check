#!/usr/bin/env python3
"""
Simple AWS Resource Cleanup Script
Delete AWS resources for serverless applications easily.
"""

# Import required libraries
import boto3  # AWS SDK for Python - lets us talk to AWS services
import sys    # System functions - lets us exit the script cleanly

# ============================================================================
# CONFIGURATION - Edit these values for your setup
# ============================================================================
# Which environment to clean up (staging or production)
ENVIRONMENT = 'staging'  # Change to 'prod' for production

# Which AWS region your resources are in
REGION = 'us-east-1'     # Change to your AWS region

# Dictionary storing all resource names
# The f-string automatically adds the environment name to each resource
# Example: if ENVIRONMENT = 'staging', lambda becomes 'staging-health-check-function'
RESOURCES = {
    'lambda': f"{ENVIRONMENT}-health-check-function",  # Lambda function name
    'role': f"{ENVIRONMENT}-health-check-function-role",  # IAM role name
    'table': f"{ENVIRONMENT}-requests-db",  # DynamoDB table name
    'logs': f"/aws/lambda/{ENVIRONMENT}-health-check-function"  # CloudWatch log group name
}

# ============================================================================
# MAIN CLEANUP LOGIC
# ============================================================================

def cleanup():
    """Delete all AWS resources."""
    
    # Create a dictionary of AWS clients (connections to AWS services)
    # Each client lets us interact with a specific AWS service
    clients = {
        'lambda': boto3.client('lambda', region_name=REGION),      # For Lambda functions
        'iam': boto3.client('iam'),                                # For IAM roles and policies
        'dynamodb': boto3.client('dynamodb', region_name=REGION),  # For DynamoDB tables
        'logs': boto3.client('logs', region_name=REGION)           # For CloudWatch logs
    }
    
    # Print header message
    print(f"\n🗑️  Cleaning up {ENVIRONMENT} environment...\n")
    
    # ========== 1. Delete Lambda function ==========
    # Lambda is the serverless function that runs your code
    try:
        # Try to delete the Lambda function
        clients['lambda'].delete_function(FunctionName=RESOURCES['lambda'])
        print(f"✓ Deleted Lambda: {RESOURCES['lambda']}")
    except:
        # If it doesn't exist, that's okay - just note it
        print(f"⊘ Lambda not found: {RESOURCES['lambda']}")
    
    # ========== 2. Delete CloudWatch logs ==========
    # CloudWatch stores all the logs from your Lambda function
    try:
        # Try to delete the log group
        clients['logs'].delete_log_group(logGroupName=RESOURCES['logs'])
        print(f"✓ Deleted Logs: {RESOURCES['logs']}")
    except:
        # If it doesn't exist, that's okay - just note it
        print(f"⊘ Logs not found: {RESOURCES['logs']}")
    
    # ========== 3. Detach and delete IAM role ==========
    # IAM role gives permissions to your Lambda function
    # We need to clean up policies before deleting the role
    try:
        # Step 3a: Detach all managed policies (AWS-provided policies)
        # Get the list of attached policies
        policies = clients['iam'].list_attached_role_policies(RoleName=RESOURCES['role'])
        # Loop through each policy and detach it
        for policy in policies.get('AttachedPolicies', []):
            clients['iam'].detach_role_policy(
                RoleName=RESOURCES['role'],
                PolicyArn=policy['PolicyArn']
            )
        
        # Step 3b: Delete all inline policies (custom policies created for this role)
        # Get the list of inline policy names
        inline = clients['iam'].list_role_policies(RoleName=RESOURCES['role'])
        # Loop through each policy name and delete it
        for policy_name in inline.get('PolicyNames', []):
            clients['iam'].delete_role_policy(
                RoleName=RESOURCES['role'],
                PolicyName=policy_name
            )
        
        # Step 3c: Delete the IAM role itself (now that it's clean)
        clients['iam'].delete_role(RoleName=RESOURCES['role'])
        print(f"✓ Deleted IAM Role: {RESOURCES['role']}")
    except:
        # If role doesn't exist, that's okay - just note it
        print(f"⊘ IAM Role not found: {RESOURCES['role']}")
    
    # ========== 4. Delete DynamoDB table ==========
    # DynamoDB is the database that stores your application data
    try:
        # Try to delete the table
        clients['dynamodb'].delete_table(TableName=RESOURCES['table'])
        print(f"✓ Deleted DynamoDB: {RESOURCES['table']}")
    except:
        # If it doesn't exist, that's okay - just note it
        print(f"⊘ DynamoDB not found: {RESOURCES['table']}")
    
    # Print completion message
    print("\n✅ Cleanup complete!\n")


# ============================================================================
# RUN THE SCRIPT
# ============================================================================

# This runs when you execute the script directly (not when imported as a module)
if __name__ == "__main__":
    # Show warning message about what will be deleted
    print("\n⚠️  WARNING: This will DELETE AWS resources!")
    print(f"   Environment: {ENVIRONMENT}")
    print(f"   Region: {REGION}\n")
    
    # Ask user to confirm before proceeding
    # .strip() removes extra spaces, .lower() converts to lowercase
    confirm = input("Type 'yes' to continue: ").strip().lower()
    
    # Check if user typed 'yes'
    if confirm == 'yes':
        # User confirmed - run the cleanup function
        cleanup()
    else:
        # User didn't type 'yes' - cancel and exit
        print("\n❌ Cancelled. Nothing was deleted.\n")
        sys.exit(0)  # Exit the script cleanly
