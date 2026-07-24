#!/bin/bash
START_HAPROXY="/usr/sbin/haproxy -f /etc/haproxy/haproxy.cfg"
LOG_FILE="/usr/local/keepalived/log/haproxy-check.log"
HAPS=`ps -C haproxy --no-header |wc -l`
date "+%Y-%m-%d %H:%M:%S" >> $LOG_FILE
echo "check haproxy status" >> $LOG_FILE
if [ $HAPS -eq 0 ];then
  echo $START_HAPROXY >> $LOG_FILE
  /usr/sbin/haproxy -f /etc/haproxy/haproxy.cfg
  sleep 3
  if [ `ps -C haproxy --no-header |wc -l` -eq 0 ];then
    echo "start haproxy failed, killall keepalived" >> $LOG_FILE
    killall keepalived
    service keepalived stop
  fi
fi
