import boto3

# Update to match a locally stored AWS profile
session = boto3.session.Session(profile_name='augmenthor')
ec2_rsrc = session.resource('ec2')
ec2_instance_id=None
# Ec2's User Data script that will be executed at the EC2 instance initialization
# Upon successful execution, it will
# install the DATADOG Agent
# install and execute the stress tool which will bring the CPU [close]to 100% utilization for 5 minutes
ec2_instance_stress_script ="""#!/bin/bash
DD_AGENT_MAJOR_VERSION=7 DD_API_KEY=<user_api_key> bash -c "$(curl -L https://raw.githubusercontent.com/DataDog/datadog-agent/master/cmd/agent/install_script.sh)"
sudo yum install stress -y
stress -c 1200 -i 1200 -d 1200 -t 300"""

s3_rsrc= session.resource('s3')

cloudwatch_clnt=session.client('cloudwatch')


def workflow():
    # EC2 instance creation
    ec2_instance_id=create_ec2()
    print("ec2_instance_id: {}".format(ec2_instance_id))
    # CloudWatch Metric Alarm
    create_cloudwatch_metric_alarm(ec2_instance_id)
    # S3 bucket creation
    create_s3_bucket("augmenthor-pd")
    # To terminate the EC2 instance programatically uncomment use the following function
    # terminate_ec2(ec2_instance_id)

def create_ec2():
    # create an EC2 instance
    try:
        instance= ec2_rsrc.create_instances(
            ImageId="ami-0915e09cc7ceee3ab",
            KeyName="KP-AWSCCPVPC-EC2-A",
            MinCount=1,
            MaxCount=1,
            InstanceType='t2.micro',
            Monitoring={'Enabled': True },
            SecurityGroups=['launch-wizard-1'],
            UserData=ec2_instance_stress_script)
        return instance[0].id
    except Exception as error:
        print(error)

def create_s3_bucket(bucketname):
    # create an SNS topic
    try:
        response = s3_rsrc.create_bucket(
            ACL='public-read-write',
            Bucket=bucketname
            #,CreateBucketConfiguration={'LocationConstraint': 'us-east-1'}
        )
        print(response)
    except Exception as error:
        print(error)


def create_cloudwatch_metric_alarm(ec2instnceid):
    # Create a CloudWatch metric alarm to monitor the CPU utilization of the newly created EC2 instance
    # and to send an SNS message to an SNS PD endpoint
    try:
        # Create alarm
        response=cloudwatch_clnt.put_metric_alarm(
            AlarmName='{}_CPU_Utilization'.format(ec2instnceid),
            ComparisonOperator='GreaterThanThreshold',
            EvaluationPeriods=1,
            MetricName='CPUUtilization',
            Namespace='AWS/EC2',
            Period=180,
            Statistic='Maximum',
            Threshold=70.0,
            ActionsEnabled=True,
            AlarmActions=[
                'arn:aws:sns:us-east-1:300354831611:CloudWatch-to-PagerDuty',
            ],
            AlarmDescription='Alarm when server CPU exceeds 70%',
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': ec2instnceid
                },
            ]
        )
        print(response)
    except Exception as error:
        print(error)


def terminate_ec2(iid):
    #terminate an EC2 instance
    instance_id=iid
    try:
        instance = ec2_rsrc.Instance(instance_id)
        response=instance.terminate()
    except Exception as error:
        print(error)


if __name__ == '__main__':
    workflow()