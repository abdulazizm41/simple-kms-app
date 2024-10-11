#!/bin/bash

PAYLOAD=`cat -`

for i in ${PAYLOAD}; do
  curl -k -XPOST "http://127.0.0.1:8000/encrypt" \
          -H "Content-Type: application/json" \
          -d'{"payload": "'${i}'"}' 2> /dev/null
  echo
  sleep 1
done
