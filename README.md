# Serverless Health Check API

A serverless health check API built with AWS Lambda, API Gateway, and DynamoDB, deployed using Terraform and GitHub Actions.

## Architecture

- **API Gateway**: HTTP API with `/health` endpoint (GET/POST)
- **Lambda Function**: Processes requests, logs to CloudWatch, saves to DynamoDB
- **DynamoDB**: Stores request data with unique IDs
- **IAM**: Least-privilege permissions for Lambda execution

## Prerequisites

1. **AWS Account** with programmatic access
2. **GitHub Repository** with the following secrets configured:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
3. **Terraform** >= 1.0 (for local development)
4. **AWS CLI** (optional, for testing)

### Setting up GitHub Secrets

1. Go to your repository → Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `AWS_ACCESS_KEY_ID`: Your AWS access key
   - `AWS_SECRET_ACCESS_KEY`: Your AWS secret key

### Optional: S3 Backend for Terraform State

Create an S3 bucket and DynamoDB table for remote state:

```bash
aws s3api create-bucket \
  --bucket your-terraform-state-bucket \
  --region us-east-1

aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

Update `terraform/backend.tf` with your bucket name.

## CI/CD Pipeline

The GitHub Actions pipeline automatically:

1. **On Push to `staging` branch**: Deploys to staging environment
2. **On Push to `main` branch**: Deploys to both staging and production
3. **Manual Workflow**: Deploy specific environment via workflow_dispatch

### Pipeline Stages

1. **Terraform Plan**: Validates and creates execution plan
2. **Staging Deploy**: Automatically deploys to staging
3. **Production Deploy**: Deploys to prod (requires manual approval in GitHub)

### Manual Approval for Production

GitHub requires environment protection rules:

1. Go to Settings → Environments → Create "production" environment
2. Enable "Required reviewers" and add yourself
3. Production deployments will now require approval

## Deployment Instructions

### Option 1: Automatic Deployment via GitHub Actions

**Deploy to Staging:**
```bash
git checkout -b staging
git push origin staging
```

**Deploy to Production:**
```bash
git checkout main
git push origin main
# Approve the production deployment in GitHub Actions UI
```

**Manual Deployment:**
1. Go to Actions → Deploy Serverless Health Check → Run workflow
2. Select environment (staging or prod)
3. Click "Run workflow"

### Option 2: Local Deployment

```bash
# Initialize Terraform
cd terraform
terraform init

# Plan deployment
terraform plan -var-file="environments/staging.tfvars"

# Apply deployment
terraform apply -var-file="environments/staging.tfvars"

# Get API endpoint
terraform output api_endpoint
```

## Testing the API

After deployment, get your API endpoint:

```bash
# From Terraform output
terraform output api_endpoint

# Or from GitHub Actions logs
```

### Test with curl

**GET Request:**
```bash
curl https://your-api-id.execute-api.us-east-1.amazonaws.com/health
```

**POST Request:**
```bash
curl -X POST https://your-api-id.execute-api.us-east-1.amazonaws.com/health \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

**Expected Response:**
```json
{
  "status": "healthy",
  "message": "Request processed and saved.",
  "request_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Verify DynamoDB Records

```bash
aws dynamodb scan \
  --table-name staging-requests-db \
  --region us-east-1
```

### Check CloudWatch Logs

```bash
aws logs tail /aws/lambda/staging-health-check-function \
  --follow \
  --region us-east-1
```

## Project Structure

```
├── .github/workflows/deploy.yml    # CI/CD pipeline
├── terraform/
│   ├── modules/                    # Reusable Terraform modules
│   │   ├── dynamodb/
│   │   ├── lambda/
│   │   └── api-gateway/
│   ├── environments/               # Environment-specific variables
│   │   ├── staging.tfvars
│   │   └── prod.tfvars
│   ├── main.tf                     # Main infrastructure
│   ├── variables.tf
│   ├── outputs.tf
│   ├── providers.tf
│   └── backend.tf
├── lambda/
│   ├── health_check.py            # Lambda function code
│   └── requirements.txt
└── README.md
```

## Design Decisions

### 1. Modular Terraform Structure
- **Why**: Reusability across environments and easier maintenance
- **Trade-off**: Slightly more complex structure but better scalability

### 2. HTTP API Gateway (v2) vs REST API
- **Why**: Simpler, cheaper, and sufficient for this use case
- **Trade-off**: Fewer features than REST API but not needed here

### 3. DynamoDB Pay-Per-Request Billing
- **Why**: Cost-effective for unpredictable/low traffic
- **Trade-off**: Slightly higher per-request cost but no idle charges

### 4. Lambda Python 3.11
- **Why**: Latest stable version with good AWS SDK support
- **Trade-off**: None, backwards compatible

### 5. CloudWatch Log Retention (7 days)
- **Why**: Balance between debugging capability and cost
- **Trade-off**: Logs expire after a week

### 6. Least-Privilege IAM
- **Why**: Security best practice, only grants necessary permissions
- **Trade-off**: None, always prefer least privilege

## Troubleshooting

### Pipeline Fails: "Error acquiring state lock"
- **Solution**: Delete the lock in DynamoDB or wait for timeout

### Lambda Function Fails
```bash
# Check logs
aws logs tail /aws/lambda/staging-health-check-function --follow

# Check function configuration
aws lambda get-function --function-name staging-health-check-function
```

### API Gateway Returns 500
- Lambda execution role may lack permissions
- Check CloudWatch logs for Lambda errors

## Cleanup

To destroy all resources:

```bash
cd terraform
terraform destroy -var-file="environments/staging.tfvars"
terraform destroy -var-file="environments/prod.tfvars"
```

## Future Enhancements

- Add API authentication (API keys or Cognito)
- Implement request rate limiting
- Add monitoring and alerting with CloudWatch Alarms
- Create custom domain name for API
- Add integration tests in CI/CD pipeline
- Implement blue-green deployments

## License

MIT
```

This is your complete solution! The key features:

✅ Multi-environment support (staging/prod)
✅ Proper naming convention (env-resource-name)
✅ Modular Terraform structure
✅ Least-privilege IAM roles
✅ Full CI/CD with GitHub Actions
✅ Manual approval for production
✅ Lambda packaging in pipeline
✅ Clear commit history structure
✅ Comprehensive documentation

Start by creating the repository structure, then commit each component step by step with clear messages like:
1. "Initial project structure"
2. "Add Lambda function code"
3. "Add DynamoDB Terraform module"
4. "Add Lambda Terraform module"
5. "Add API Gateway Terraform module"
6. "Add main Terraform configuration"
7. "Add GitHub Actions CI/CD pipeline"
8. "Add comprehensive README
