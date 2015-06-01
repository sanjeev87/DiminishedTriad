#!/bin/bash

max=26
y=0
while [  $((y)) -lt $((max)) ]; do
    for x in {a..z}; do
        let z=$(( ( RANDOM % 6 )  + 1 ))
        curl "http://localhost:5000$z/set?key=$x$y&value=$x$y" > op.txt 2>&1 
    done
    w=$((y%5))
    if [ $w -eq 0 ]
    then
        echo "key set ${y}%"
    fi
    y=$((y+1))
done

y=0
while [  $((y)) -lt $((max)) ]; do
    for x in {a..z}; do
        let z=$(( ( RANDOM % 6 )  + 1 ))
        # curl "http://localhost:5000$z/get?key=$x$y" > op.txt 2>&1
        
        op=$(curl "http://localhost:5000$z/get?key=$x$y" 2>er.txt)
        # echo ".${x}${y}"
        # echo "${op}" 
        if [ "$op" != "\"$x$y\"" ]
        then
            echo "MISMATCH, got: $op expected: $x$y"
        fi
    done
    w=$((y%5))
    if [ $w -eq 0 ]
    then
        echo "key get ${y}%"
    fi
    y=$((y+1))
done

echo "TEST OK."
