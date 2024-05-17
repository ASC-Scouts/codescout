#!/usr/bin/bash

CODESCOUT=../codescout/codescout.py

for CODE in soleil musical
do
    $CODESCOUT -m "Un castor joue avec:et comme les autres" -c $CODE -b 3 -s code_${CODE}.png -i 2 --legende "vincent.fortin@gmail.com"
    $CODESCOUT -m "Un castor joue avec:et comme les autres" -c $CODE -b 3 -s code_${CODE}_decode.png --decoder
done
