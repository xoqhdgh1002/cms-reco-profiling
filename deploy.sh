#!/bin/bash

DEPLOY_PATH=$1
rsync -rR --progress --ignore-existing --include "*/"  --include="*.sql3" --exclude="*" results/igprof/./* $DEPLOY_PATH/
