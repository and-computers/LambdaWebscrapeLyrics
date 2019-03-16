#!/bin/bash

echo "beginning deployment script"

echo "install requirements.txt"
mkdir lambda_deployment_package
pip install -r requirements.txt --target lambda_deployment_package
echo "copying lambda function to deployment package"
cp  lambda_handler.py lambda_deployment_package/

echo "removing provided AWS libraries, botocore and boto3"

rm -r lambda_deployment_package/boto3* 
rm -r lambda_deployment_package/botocore*

echo "zipping deployment package"
zip -r9 lambda_deployment_package.zip lambda_deployment_package

echo "removing package folder"
rm -r lambda_deployment_package

ACCESS_KEY=$1
SECRET_KEY=$2
RESOURCE_ROLE=$3

AWS_ACCESS_KEY_ID=$ACCESS_KEY AWS_SECRET_ACCESS_KEY=$SECRET_KEY aws lambda create-function \
	--function-name "webscrape-lyrics" \
	--handler "lambda_handler.handler" \
	--timeout 120 \
	--memory-size 256 \
	--zip-file fileb://lambda_deployment_package.zip \
	--runtime python3.6 \
	--description "lambda for scheduling webscrape lyrics" \
	--environment "Variables={TestVar=TestValue,TestVar2=TestValue2}" \
	--role $RESOURCE_ROLE