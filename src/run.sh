#!/bin/bash

while read LINE
do
        export $LINE
done < .env

python main.py

