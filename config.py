"""
CloudFormation Deployment Configuration
"""

# AWS Credentials

# Stack Configuration
STACKS = {
    'vpc-infrastructure': {
        'template': 'templates/vpc.yaml',
        'parameters': {
            'VpcCIDR': '10.0.0.0/16',
            'PublicSubnet1CIDR': '10.0.1.0/24',
            'PublicSubnet2CIDR': '10.0.2.0/24',
            'PrivateSubnet1CIDR': '10.0.10.0/24',
            'PrivateSubnet2CIDR': '10.0.11.0/24'
        },
        'tags': {
            'Environment': 'Production',
            'Project': 'Infrastructure',
            'ManagedBy': 'CloudFormation'
        }
    },
    'application-tier': {
        'template': 'templates/application.yaml',
        'parameters': {
            'InstanceType': 't3.medium',
            'KeyName': 'production-key',
            'MinSize': '2',
            'MaxSize': '10',
            'DesiredCapacity': '4'
        },
        'tags': {
            'Environment': 'Production',
            'Tier': 'Application'
        }
    },
    'database-tier': {
        'template': 'templates/database.yaml',
        'parameters': {
            'DBInstanceClass': 'db.t3.large',
            'DBName': 'productiondb',
            'MasterUsername': 'admin',
            'AllocatedStorage': '100'
        },
        'tags': {
            'Environment': 'Production',
            'Tier': 'Database'
        }
    }
}

# Deployment Settings
CAPABILITIES = ['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']
TIMEOUT_MINUTES = 30
ENABLE_TERMINATION_PROTECTION = True

# S3 Bucket for Templates
TEMPLATE_BUCKET = 'cloudformation-templates-prod'
TEMPLATE_PREFIX = 'stacks/'

# SNS Topic for Notifications
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-2:123456789012:cloudformation-events'
