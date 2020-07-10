#!/bin/bash

cd ~/scraper/
git pull origin master
conda activate scraper-10x10
scrapyd-deploy -a

