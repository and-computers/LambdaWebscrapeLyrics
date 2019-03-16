#!/bin/bash

echo "beginning deployment script"

echo "install requirements.txt"
mkdir lambda_deployment_package
cd lambda_deployment_package
pip install --no-deps -r ../requirements.txt --target .
echo "copying lambda function to deployment package"
#cp  lambda_handler.py lambda_deployment_package/


# echo "removing provided AWS libraries, botocore and boto3"

# rm -r lambda_deployment_package/boto3* 
# rm -r lambda_deployment_package/botocore*
# rm -r lambda_deployment_package/tox*


echo "zipping deployment package"
zip -r9 ../function.zip .
# zip -r9 lambda_deployment_package.zip lambda_deployment_package
cd ../
zip -g function.zip lambda_handler.py


# echo "removing package folder"
# rm -r lambda_deployment_package

ACCESS_KEY=$1
SECRET_KEY=$2
RESOURCE_ROLE=$3

AWS_ACCESS_KEY_ID=$ACCESS_KEY AWS_SECRET_ACCESS_KEY=$SECRET_KEY AWS_DEFAULT_REGION="us-east-2" aws lambda create-function \
	--function-name "webscrape-lyrics" \
	--handler "lambda_handler.handler" \
	--timeout 120 \
	--memory-size 256 \
	--zip-file fileb://function.zip \
	--runtime python3.6 \
	--description "lambda for scheduling webscrape lyrics" \
	--environment "Variables={TestVar=TestValue,TestVar2=TestValue2}" \
	--role $RESOURCE_ROLE