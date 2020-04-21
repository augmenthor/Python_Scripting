# AWS-PagerDuty-Datadog Integration

## Applied Python Scripting
### Python script to provision 50 users into a PagerDuty instance

CreateUsersIntoPagerDutyInstance.py uses a csv file (/data/pdusers.csv) to upload 50 records of fictitious users 
in a Pager Duty account.
The inital structure of the record is : 'name', 'email', 'role'.
Upon a successful creation of a record in Pager Duty account, the returned user ID is appended to the
corresponding record of the csv file, making the record structure as:'name', 'email', 'role', 'id'
The use a csv file having an id on the fourth position of any of the records will result in updating those user records
into the Pager Duty account.

## Applied AWS and Monitoring Configurations
### Spin up an AWS environment using free tier resources
AWSScripting.py contains scripts to create EC2, S3, SNS (Topic, Subscription), CloudWatch (Alarm) 
in an AWS free tier account
### Spin Up Datadog monitoring solution and configure it to monitor your AWS environment
AWSScripting.py creates an EC2 instance which installs a Datadog agent on the initialization script executed as User 
Data script.
Using the Datadog admin console, an AWS integration has been set up with Role Delegation authentication.
In the AWS admin console, a specific role has been created to allow for Datadog integration.
### Integrate your AWS monitoring tool environments with your PagerDuty Environment
AWSScripting.py creates an EC2 instance which installs and executes the  the 'stress' Linux tool. This tool will bring
the CPU utilisation close to 100% for about 5 minutes.
The same script creates a CloudWatch metric alert whcih sends an alert to a SNS topic when CPU utilisation threshold 
reaches 70%. The SNS topic is subscribed by a PagerDuty endpoint which creates a an alert in PD and alerts the team 
members on schedule.
Upon the resolution of the PD alert a message is recieved  by the Cloudwatch Alert via the same SNS topic/subscription.
 
