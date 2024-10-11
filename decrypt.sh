#!/bin/bash

SECRET=${@}

for i in ${SECRET}; do
  RESULT=$(curl -k -XPOST "http://192.168.56.103:8000/decrypt" \
          -H "Content-Type: application/json" \
          -d'{"payload": '${i}'}' 2> /dev/null)
  echo ${RESULT}
done
