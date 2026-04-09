"""
CloudFormation Template Manager
Validate and manage CloudFormation templates
"""

import boto3
import json
import yaml
from config import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    TEMPLATE_BUCKET,
    TEMPLATE_PREFIX
)

class TemplateManager:
    def __init__(self):
        self.cf_client = boto3.client(
            'cloudformation',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
    
    def validate_template(self, template_path):
        """
        Validate a CloudFormation template
        """
        try:
            with open(template_path, 'r') as f:
                template_body = f.read()
            
            response = self.cf_client.validate_template(
                TemplateBody=template_body
            )
            
            print(f"✓ Template is valid: {template_path}")
            
            # Print template details
            if 'Parameters' in response:
                print(f"  Parameters: {len(response['Parameters'])}")
            if 'Capabilities' in response:
                print(f"  Required capabilities: {response['Capabilities']}")
            
            return True
        
        except Exception as e:
            print(f"✗ Template validation failed: {str(e)}")
            return False
    
    def upload_template_to_s3(self, template_path, stack_name):
        """
        Upload template to S3 bucket
        """
        try:
            s3_key = f"{TEMPLATE_PREFIX}{stack_name}.yaml"
            
            with open(template_path, 'rb') as f:
                self.s3_client.put_object(
                    Bucket=TEMPLATE_BUCKET,
                    Key=s3_key,
                    Body=f
                )
            
            template_url = f"https://{TEMPLATE_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
            
            print(f"✓ Template uploaded to S3: {template_url}")
            return template_url
        
        except Exception as e:
            print(f"✗ Error uploading template: {str(e)}")
            return None
    
    def get_template_summary(self, template_path):
        """
        Get summary of CloudFormation template
        """
        try:
            with open(template_path, 'r') as f:
                template_body = f.read()
            
            response = self.cf_client.get_template_summary(
                TemplateBody=template_body
            )
            
            print(f"\nTemplate Summary for {template_path}:")
            print(f"  Version: {response.get('Version', 'N/A')}")
            print(f"  Resource Types: {len(response.get('ResourceTypes', []))}")
            
            if 'ResourceTypes' in response:
                print("  Resources:")
                for resource_type in response['ResourceTypes']:
                    print(f"    - {resource_type}")
            
            return response
        
        except Exception as e:
            print(f"✗ Error getting template summary: {str(e)}")
            return None
    
    def estimate_template_cost(self, template_path, parameters):
        """
        Estimate cost of deploying template
        """
        try:
            with open(template_path, 'r') as f:
                template_body = f.read()
            
            # Convert parameters to CloudFormation format
            cf_parameters = [
                {'ParameterKey': k, 'ParameterValue': str(v)}
                for k, v in parameters.items()
            ]
            
            response = self.cf_client.estimate_template_cost(
                TemplateBody=template_body,
                Parameters=cf_parameters
            )
            
            cost_url = response.get('Url', '')
            print(f"✓ Cost estimate available at: {cost_url}")
            
            return cost_url
        
        except Exception as e:
            print(f"✗ Error estimating cost: {str(e)}")
            return None
    
    def convert_json_to_yaml(self, json_template_path, yaml_output_path):
        """
        Convert JSON template to YAML
        """
        try:
            with open(json_template_path, 'r') as f:
                template = json.load(f)
            
            with open(yaml_output_path, 'w') as f:
                yaml.dump(template, f, default_flow_style=False)
            
            print(f"✓ Converted {json_template_path} to {yaml_output_path}")
            return True
        
        except Exception as e:
            print(f"✗ Error converting template: {str(e)}")
            return False
