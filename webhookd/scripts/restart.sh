#!/bin/bash

cd ~/scraper/
killall scrapyd
source ~/anaconda3/etc/profile.d/conda.sh
conda activate scraper-10x10
nohup scrapyd &
scrapyd-deploy naver_scrap -p naver_scrap
scrapyd-deploy lightweight_scrap -p lightweight_scrap
cd ~/scraper/webhookd/
killall webhookd
nohup webhookd -listen-addr ":9000" &
