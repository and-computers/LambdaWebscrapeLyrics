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


ISNEW=$1
RESOURCE_ROLE=$2
ALIAS=$3

FNAME=$4
HANDLER=$5
TIMEOUT=$6
MEMSIZE=$7
DESC=$8
ENV=$9
RUNTIME=${10}
REGION=${11}


if [ $ISNEW == "yes" ]
then
echo "deploying brand new function"
aws lambda create-function \
	--function-name $FNAME \
	--handler $HANDLER \
	--timeout $TIMEOUT \
	--memory-size $MEMSIZE \
	--zip-file fileb://function.zip \
	--runtime $RUNTIME \
	--description $DESC \
	--environment $ENV \
	--role $RESOURCE_ROLE \
	--revision-id $ALIAS

elif [ $ISNEW == "no" ]
then
echo "updating function"
# update function code
aws lambda update-function-code \
	--function-name "${FNAME}" \
	--zip-file fileb://function.zip \
	--publish 

# update function configuration
aws lambda update-function-configuration \
	--function-name "$FNAME" \
	--handler "$HANDLER" \
	--timeout "$TIMEOUT" \
	--memory-size $MEMSIZE \
	--runtime "${RUNTIME}" \
	--description "${DESC}" \
	--environment "${ENV}" \
	--role "${RESOURCE_ROLE}" \
	--revision-id $ALIAS

else
echo "not a new function. but not an old function. this line should not be hit."
fi






