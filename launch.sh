#!/bin/bash

SCRAMBLING_KEY="mySuperSecretScramblingKey"

##### SEND A SMALL FILE #####
python3 main.py s $SCRAMBLING_KEY public.pem secret_service_account.json samples/file.txt
#python3 main.py r $SCRAMBLING_KEY private.pem secret_service_account.json destDir

##### SEND A BIGGER FILE #####
#python3 main.py s $SCRAMBLING_KEY public.pem secret_service_account.json samples/image1.jpeg
#python3 main.py r $SCRAMBLING_KEY private.pem secret_service_account.json destDir

############### PARAMS ###############
# Params:
# - direction: <s or r> send or receive
# - scramblingKey
# - rsaKeyFile
# - credentialsFile
# - messageFile
############### PARAMS ###############
