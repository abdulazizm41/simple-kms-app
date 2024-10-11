#!/bin/bash

SECRET=${@}

for i in ${SECRET}; do
  RESULT=$(curl -k -XPOST "http://127.0.0.1:8000/decrypt" \
          -H "Content-Type: application/json" \
          -d'{"payload": '${i}'}' 2> /dev/null)
  echo ${RESULT}
done
