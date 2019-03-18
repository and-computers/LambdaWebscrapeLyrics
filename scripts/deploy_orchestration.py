import os
import configparser
import subprocess
import sys


ACCESS_KEY = sys.argv[1]
SECRET_KEY = sys.argv[2]
RESOURCE_ROLE = sys.argv[3]


cfg = configparser.ConfigParser()
cfg.read('deployment_config.ini')

import pdb
pdb.set_trace()

# parse lambda configuration parameters
for config_tuple in cfg.items('configuration'):
    pass


# https://stackoverflow.com/questions/5466451/how-can-i-print-literal-curly-brace-characters-in-python-string-and-also-use-fo#5466478
VARS_STR_TEMPLATE = "Variables={{{}}}"
env_vars = ""
for config_tuple in cfg.items('environment'):
    env_vars += "{k}={v},".format(k=config_tuple[0], v=config_tuple[1])

VARS_STR = VARS_STR_TEMPLATE.format(env_vars)
print(VARS_STR)


def is_func_new(funcname):
	"""
	determine if function being deployed is brand new or just needs updates
	"""
    bashCommand = "aws lambda list-functions"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    out_json = json.loads(output)
    for function_params in out_json['Functions']:
        if str(funcname) == str(function_params['FunctionName']):
            return False
    return True

def deploy_brand_new_lambda():
	"""
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
	"""

	bashCommand = "bash scripts/aws-lambda-deploy.sh \
	{AWS_ACCESS_KEY} \
	{AWS_SECRET_KEY} \
	{AWS_LAMBDA_ROLE} \
	{isnew} \
	{funcname} {handler} {timeout} {memsize} {desc} {env} {runtime} {region}".format(
		AWS_ACCESS_KEY=ACCESS_KEY,
		AWS_SECRET_KEY=SECRET_KEY,
		AWS_LAMBDA_ROLE=RESOURCE_ROLE,
		isnew='yes',
		funcname=funcname,
		desc=desc,
		runtime=runtime,
		handler=handler,
		region=region,
		timeout=timeout,
		mem=memory,
		env=VARS_STR
		)

	process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
	output, error = process.communicate()


def update_existing_lambda():
	bashCommand = "bash scripts/aws-lambda-deploy.sh \
	{AWS_ACCESS_KEY} \
	{AWS_SECRET_KEY} \
	{AWS_LAMBDA_ROLE} \
	{isnew} \
	{funcname} {handler} {timeout} {memsize} {desc} {env} {runtime} {region}".format(
		AWS_ACCESS_KEY=ACCESS_KEY,
		AWS_SECRET_KEY=SECRET_KEY,
		AWS_LAMBDA_ROLE=RESOURCE_ROLE,
		isnew='no',
		funcname=funcname,
		desc=desc,
		runtime=runtime,
		handler=handler,
		region=region,
		timeout=timeout,
		mem=memory,
		env=VARS_STR
		)

	process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
	output, error = process.communicate()

if is_func_new():
	deploy_brand_new_lambda()
else:
	update_existing_lambda()



