# EMS-Batch



## Getting started

EMS batch process base

## Fix config.ini

1. edit config.ini file
2. update job_id to your job name
3. setup frequency
4. setup source and dest source 

## Fix docker compose file

change: image: "batch-scheduler:v1.0"

## Run command

```
cd ~/project/ems-batch
docker compose up -d
```