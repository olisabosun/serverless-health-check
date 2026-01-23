#!/bin/bash
ENV="staging"

echo "Deleting Lambda function..."
aws lambda delete-function --function-name ${ENV}-health-check-function --region us-east-1 2>/dev/null || true

echo "Deleting Log Group..."
aws logs delete-log-group --log-group-name /aws/lambda/${ENV}-health-check-function --region us-east-1 2>/dev/null || true

echo "Detaching policies from IAM role..."
for policy in $(aws iam list-attached-role-policies --role-name ${ENV}-health-check-function-role --query 'AttachedPolicies[].PolicyArn' --output text 2>/dev/null); do
  aws iam detach-role-policy --role-name ${ENV}-health-check-function-role --policy-arn $policy
done

echo "Deleting inline policies..."
for policy in $(aws iam list-role-policies --role-name ${ENV}-health-check-function-role --query 'PolicyNames[]' --output text 2>/dev/null); do
  aws iam delete-role-policy --role-name ${ENV}-health-check-function-role --policy-name $policy
done

echo "Deleting IAM role..."
aws iam delete-role --role-name ${ENV}-health-check-function-role 2>/dev/null || true

echo "Deleting DynamoDB table..."
aws dynamodb delete-table --table-name ${ENV}-requests-db --region us-east-1 2>/dev/null || true

echo "Cleanup complete!"
