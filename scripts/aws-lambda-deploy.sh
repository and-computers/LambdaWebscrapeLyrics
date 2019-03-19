#!/bin/bash

echo "beginning deployment script"

echo "install requirements.txt"
mkdir lambda_deployment_package
cd lambda_deployment_package
# install s3fs seperately because the dependencies are already in the lamdba env
pip install --no-deps --no-cache-dir --compile s3fs --target .
pip install --no-cache-dir --compile -r ../requirements.txt --target .


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

ISNEW=$4

FNAME=$5
HANDLER=$6
TIMEOUT=$7
MEMSIZE=$8
DESC=$9
ENV=${10}
RUNTIME=${11}
REGION=${12}


if [ $ISNEW == "yes" ]
then
echo "deploying brand new function"
AWS_ACCESS_KEY_ID=$ACCESS_KEY AWS_SECRET_ACCESS_KEY=$SECRET_KEY AWS_DEFAULT_REGION=$REGION aws lambda create-function \
	--function-name $FNAME \
	--handler $HANDLER \
	--timeout $TIMEOUT \
	--memory-size $MEMSIZE \
	--zip-file fileb://function.zip \
	--runtime $RUNTIME \
	--description $DESC \
	--environment $ENV \
	--role $RESOURCE_ROLE

elif [ $ISNEW == "no" ]
then
echo "updating function"
# update function code
# AWS_ACCESS_KEY_ID=$ACCESS_KEY AWS_SECRET_ACCESS_KEY=$SECRET_KEY AWS_DEFAULT_REGION=$REGION aws lambda update-function-code \
aws lambda update-function-code \
	--function-name "${FNAME}" \
	--zip-file fileb://function.zip \
	--publish 

# update function configuration
# AWS_ACCESS_KEY_ID=$ACCESS_KEY AWS_SECRET_ACCESS_KEY=$SECRET_KEY AWS_DEFAULT_REGION=$REGION aws lambda update-function-configuration \
aws lambda update-function-configuration \
	--function-name "$FNAME" \
	--handler "$HANDLER" \
	--timeout "$TIMEOUT" \
	--memory-size $MEMSIZE \
	--runtime "python3.6" \
	--description "${DESC}" \
	--environment "${ENV}" \
	--role "${RESOURCE_ROLE}"

else
echo "not a new function. but not an old function. this line should not be hit."
fi






