# SSM Parameters for secrets
resource "aws_ssm_parameter" "secret_key" {
  name  = "/3mtt-chatbot/SECRET_KEY"
  type  = "SecureString"
  value = var.secret_key
  
  tags = {
    Environment = "production"
    Application = "3mtt-chatbot"
  }
}

resource "aws_ssm_parameter" "openai_api_key" {
  name  = "/3mtt-chatbot/OPENAI_API_KEY"
  type  = "SecureString"
  value = var.openai_api_key
  
  tags = {
    Environment = "production"
    Application = "3mtt-chatbot"
  }
}

resource "aws_ssm_parameter" "sentry_dsn" {
  name  = "/3mtt-chatbot/SENTRY_DSN"
  type  = "SecureString"
  value = var.sentry_dsn
  
  tags = {
    Environment = "production"
    Application = "3mtt-chatbot"
  }
}