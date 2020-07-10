#!/bin/bash

cd ~/scraper/
git pull origin master
source ~/anaconda3/etc/profile.d/conda.sh
conda activate scraper-10x10
scrapyd-deploy -a

