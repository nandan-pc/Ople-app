#!/bin/bash

chmod 755 ./service_setup.sh
chmod 755 ./service_api_calls.sh

mkdir logs

pwd=$PWD
$pwd/service_setup.sh | tee ./logs/setup.log
$pwd/service_api_calls.sh | tee ./logs/api_calls.log

