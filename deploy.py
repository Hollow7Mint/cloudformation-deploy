"""
CloudFormation Stack Deployment Script
AWS_ACCESS_KEY_ID = "AKIA2CCBUCJZ5EYRYKF7"
AWS_SECRET_ACCESS_KEY = "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"
AWS_REGION = "us-east-2"

Deploy and manage CloudFormation stacks
"""

import boto3
import time
import json
from datetime import datetime
from config import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    STACKS
)
from template_manager import TemplateManager

class CloudFormationDeployer:
    def __init__(self):
        self.cf_client = boto3.client(
            'cloudformation',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        self.template_manager = TemplateManager()
    
    def deploy_stack(self, stack_name, template_path, parameters, tags):
        """
        Deploy or update a CloudFormation stack
        """
        print(f"\n{'='*70}")
        print(f"Deploying stack: {stack_name}")
        print(f"{'='*70}")
        
        # Read template
        with open(template_path, 'r') as f:
            template_body = f.read()
        
        # Convert parameters dict to CloudFormation format
        cf_parameters = [
            {'ParameterKey': k, 'ParameterValue': str(v)}
            for k, v in parameters.items()
        ]
        
        # Convert tags dict to CloudFormation format
        cf_tags = [
            {'Key': k, 'Value': v}
            for k, v in tags.items()
        ]
        
        try:
            # Check if stack exists
            try:
                self.cf_client.describe_stacks(StackName=stack_name)
                stack_exists = True
                print(f"Stack {stack_name} exists. Updating...")
            except self.cf_client.exceptions.ClientError:
                stack_exists = False
                print(f"Stack {stack_name} does not exist. Creating...")
            
            if stack_exists:
                # Update stack
                response = self.cf_client.update_stack(
                    StackName=stack_name,
                    TemplateBody=template_body,
                    Parameters=cf_parameters,
                    Capabilities=CAPABILITIES,
                    Tags=cf_tags
                )
                action = 'UPDATE'
            else:
                # Create stack
                response = self.cf_client.create_stack(
                    StackName=stack_name,
                    TemplateBody=template_body,
                    Parameters=cf_parameters,
                    Capabilities=CAPABILITIES,
                    Tags=cf_tags,
                    TimeoutInMinutes=TIMEOUT_MINUTES,
                    EnableTerminationProtection=ENABLE_TERMINATION_PROTECTION
                )
                action = 'CREATE'
            
            print(f"Stack {action} initiated: {response['StackId']}")
            
            # Wait for stack operation to complete
            self.wait_for_stack(stack_name, action)
            
            return True
        
        except self.cf_client.exceptions.ClientError as e:
            error_message = e.response['Error']['Message']
            if 'No updates are to be performed' in error_message:
                print(f"✓ Stack {stack_name} is already up to date")
                return True
            else:
                print(f"✗ Error deploying stack: {error_message}")
                return False
        
        except Exception as e:
            print(f"✗ Unexpected error: {str(e)}")
            return False
    
    def wait_for_stack(self, stack_name, action):
        """
        Wait for stack operation to complete
        """
        if action == 'CREATE':
            waiter = self.cf_client.get_waiter('stack_create_complete')
            status = 'CREATE_COMPLETE'
        else:
            waiter = self.cf_client.get_waiter('stack_update_complete')
            status = 'UPDATE_COMPLETE'
        
        print(f"Waiting for stack {action} to complete...")
        
        try:
            waiter.wait(StackName=stack_name)
            print(f"✓ Stack {action} completed successfully")
            
            # Get stack outputs
            self.print_stack_outputs(stack_name)
            
        except Exception as e:
            print(f"✗ Stack {action} failed: {str(e)}")
            self.print_stack_events(stack_name)
    
    def print_stack_outputs(self, stack_name):
        """
        Print stack outputs
        """
        try:
            response = self.cf_client.describe_stacks(StackName=stack_name)
            stack = response['Stacks'][0]
            
            if 'Outputs' in stack and stack['Outputs']:
                print("\nStack Outputs:")
                for output in stack['Outputs']:
                    print(f"  {output['OutputKey']}: {output['OutputValue']}")
                    if 'Description' in output:
                        print(f"    Description: {output['Description']}")
        
        except Exception as e:
            print(f"Error getting stack outputs: {str(e)}")
    
    def print_stack_events(self, stack_name, limit=10):
        """
        Print recent stack events
        """
        try:
            response = self.cf_client.describe_stack_events(StackName=stack_name)
            events = response['StackEvents'][:limit]
            
            print(f"\nRecent stack events (last {limit}):")
            for event in events:
                timestamp = event['Timestamp']
                resource = event['LogicalResourceId']
                status = event['ResourceStatus']
                reason = event.get('ResourceStatusReason', '')
                
                print(f"  [{timestamp}] {resource}: {status}")
                if reason:
                    print(f"    Reason: {reason}")
        
        except Exception as e:
            print(f"Error getting stack events: {str(e)}")
    
    def delete_stack(self, stack_name):
        """
        Delete a CloudFormation stack
        """
        print(f"\nDeleting stack: {stack_name}")
        
        try:
            # Disable termination protection
            self.cf_client.update_termination_protection(
                StackName=stack_name,
                EnableTerminationProtection=False
            )
            
            # Delete stack
            self.cf_client.delete_stack(StackName=stack_name)
            
            print("Waiting for stack deletion...")
            waiter = self.cf_client.get_waiter('stack_delete_complete')
            waiter.wait(StackName=stack_name)
            
            print(f"✓ Stack {stack_name} deleted successfully")
            return True
        
        except Exception as e:
            print(f"✗ Error deleting stack: {str(e)}")
            return False
    
    def deploy_all_stacks(self):
        """
        Deploy all configured stacks
        """
        print("=" * 70)
        print("Deploying all CloudFormation stacks")
        print(f"Region: {AWS_REGION}")
        print("=" * 70)
        
        results = {}
        
        for stack_name, config in STACKS.items():
            success = self.deploy_stack(
                stack_name,
                config['template'],
                config['parameters'],
                config['tags']
            )
            results[stack_name] = success
        
        # Print summary
        print("\n" + "=" * 70)
        print("Deployment Summary:")
        print("=" * 70)
        
        for stack_name, success in results.items():
            status = "✓ SUCCESS" if success else "✗ FAILED"
            print(f"{status}: {stack_name}")
        
        return results

if __name__ == "__main__":
    deployer = CloudFormationDeployer()
    deployer.deploy_all_stacks()
# Last sync: 2026-04-29 07:59:30 UTC