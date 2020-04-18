import boto3

session = boto3.session.Session(profile_name='augmenthor')
ec2= session.resource('ec2')
# create an EC2 instance
'''
instance= ec2.create_instances(
    ImageId="ami-0915e09cc7ceee3ab",
    MinCount=1,
    MaxCount=1,
    InstanceType='t2.micro')
print(instance[0].id)
'''

#terminate an EC2 instance
instance_id="i-0d2209247c5859ff3"
instance = ec2.Instance(instance_id)
response=instance.terminate()
print(response)

