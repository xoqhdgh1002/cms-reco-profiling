#!/bin/bash

DEPLOY_PATH=$1
rsync -rR --progress --include "*/"  --include="*.sql3" --exclude="*" results/igprof/./* $DEPLOY_PATH/
