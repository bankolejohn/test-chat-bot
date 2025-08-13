#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
AWS_REGION=${AWS_REGION:-us-east-1}
TERRAFORM_STATE_BUCKET="3mtt-chatbot-terraform-state"

echo -e "${GREEN}🚀 Starting AWS deployment for 3MTT Chatbot${NC}"

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}📋 Checking prerequisites...${NC}"
    
    command -v aws >/dev/null 2>&1 || { echo -e "${RED}❌ AWS CLI is required but not installed.${NC}" >&2; exit 1; }
    command -v terraform >/dev/null 2>&1 || { echo -e "${RED}❌ Terraform is required but not installed.${NC}" >&2; exit 1; }
    command -v docker >/dev/null 2>&1 || { echo -e "${RED}❌ Docker is required but not installed.${NC}" >&2; exit 1; }
    
    # Check AWS credentials
    aws sts get-caller-identity >/dev/null 2>&1 || { echo -e "${RED}❌ AWS credentials not configured.${NC}" >&2; exit 1; }
    
    echo -e "${GREEN}✅ Prerequisites check passed${NC}"
}

# Create S3 bucket for Terraform state
create_state_bucket() {
    echo -e "${YELLOW}🪣 Creating Terraform state bucket...${NC}"
    
    if aws s3 ls "s3://${TERRAFORM_STATE_BUCKET}" 2>&1 | grep -q 'NoSuchBucket'; then
        aws s3 mb "s3://${TERRAFORM_STATE_BUCKET}" --region ${AWS_REGION}
        aws s3api put-bucket-versioning \
            --bucket ${TERRAFORM_STATE_BUCKET} \
            --versioning-configuration Status=Enabled
        aws s3api put-bucket-encryption \
            --bucket ${TERRAFORM_STATE_BUCKET} \
            --server-side-encryption-configuration '{
                "Rules": [
                    {
                        "ApplyServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "AES256"
                        }
                    }
                ]
            }'
        echo -e "${GREEN}✅ Terraform state bucket created${NC}"
    else
        echo -e "${GREEN}✅ Terraform state bucket already exists${NC}"
    fi
}

# Deploy infrastructure
deploy_infrastructure() {
    echo -e "${YELLOW}🏗️ Deploying infrastructure with Terraform...${NC}"
    
    cd terraform
    
    # Initialize Terraform
    terraform init
    
    # Plan deployment
    terraform plan -out=tfplan
    
    # Apply deployment
    terraform apply tfplan
    
    # Get outputs
    ECR_REPOSITORY_URL=$(terraform output -raw ecr_repository_url)
    ALB_DNS_NAME=$(terraform output -raw alb_dns_name)
    
    echo -e "${GREEN}✅ Infrastructure deployed successfully${NC}"
    echo -e "${GREEN}📦 ECR Repository: ${ECR_REPOSITORY_URL}${NC}"
    echo -e "${GREEN}🌐 Load Balancer: ${ALB_DNS_NAME}${NC}"
    
    cd ..
}

# Build and push Docker image
build_and_push_image() {
    echo -e "${YELLOW}🐳 Building and pushing Docker image...${NC}"
    
    # Get ECR login token
    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPOSITORY_URL}
    
    # Build image
    docker build -t 3mtt-chatbot:latest .
    
    # Tag image
    docker tag 3mtt-chatbot:latest ${ECR_REPOSITORY_URL}:latest
    docker tag 3mtt-chatbot:latest ${ECR_REPOSITORY_URL}:$(git rev-parse --short HEAD)
    
    # Push image
    docker push ${ECR_REPOSITORY_URL}:latest
    docker push ${ECR_REPOSITORY_URL}:$(git rev-parse --short HEAD)
    
    echo -e "${GREEN}✅ Docker image pushed successfully${NC}"
}

# Update ECS service
update_ecs_service() {
    echo -e "${YELLOW}🔄 Updating ECS service...${NC}"
    
    aws ecs update-service \
        --cluster 3mtt-chatbot \
        --service 3mtt-chatbot \
        --force-new-deployment \
        --region ${AWS_REGION}
    
    echo -e "${YELLOW}⏳ Waiting for deployment to complete...${NC}"
    aws ecs wait services-stable \
        --cluster 3mtt-chatbot \
        --services 3mtt-chatbot \
        --region ${AWS_REGION}
    
    echo -e "${GREEN}✅ ECS service updated successfully${NC}"
}

# Health check
health_check() {
    echo -e "${YELLOW}🏥 Performing health check...${NC}"
    
    sleep 30  # Wait for service to be ready
    
    if curl -f http://${ALB_DNS_NAME}/health; then
        echo -e "${GREEN}✅ Health check passed${NC}"
        echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
        echo -e "${GREEN}🌐 Application URL: http://${ALB_DNS_NAME}${NC}"
    else
        echo -e "${RED}❌ Health check failed${NC}"
        exit 1
    fi
}

# Main deployment flow
main() {
    check_prerequisites
    create_state_bucket
    deploy_infrastructure
    build_and_push_image
    update_ecs_service
    health_check
}

# Run main function
main "$@"