import boto3

session = boto3.session.Session(profile_name='augmenthor')
s3= session.resource('s3')
bucket_name = "augmenthor-py"
try:
    response=s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint':'us-east-1'})
    print(response)
except Exception as error:
    print(error)