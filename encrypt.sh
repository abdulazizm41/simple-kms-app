#!/bin/bash

PAYLOAD=`cat -`

for i in ${PAYLOAD}; do
  curl -k -XPOST "http://192.168.56.103:8000/encrypt" \
          -H "Content-Type: application/json" \
          -d'{"payload": "'${i}'"}' 2> /dev/null
  echo
  sleep 1
done
