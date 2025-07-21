# AWS Elastic Beanstalk expects 'application' variable
from app import app

# Elastic Beanstalk looks for 'application' callable
application = app

if __name__ == "__main__":
    application.run()