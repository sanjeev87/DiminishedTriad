#!/bin/bash

for y in {1..99}
do
for x in {a..z}
do
	let z=$(( ( RANDOM % 6 )  + 1 ))
	echo "$z $x$y"
	curl "http://localhost:5000$z/set?key=$x$y&value=$x$y"
done
done

for y in {1..99}
do
for x in {a..z}
do
	let z=$(( ( RANDOM % 6 )  + 1 ))
	echo "$z $x$y"
	curl "http://localhost:5000$z/get?key=$x$y"
	echo "\n"
done
done
