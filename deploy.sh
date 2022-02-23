#!/bin/bash

DEPLOY_PATH=/eos/project/c/cmsweb/www/reco-prof/cgi-bin/data/releases
rsync -rR --progress --ignore-existing --include "*/"  --include="*.sql3" --exclude="*" results/igprof/./* $DEPLOY_PATH/
