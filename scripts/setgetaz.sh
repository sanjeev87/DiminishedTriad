#!/bin/bash
for x in {a..z}
do
       echo `curl "http://localhost:50001/set?key=$x&value=$x"`
done
for x in {a..z}
do
       echo `curl "http://localhost:50001/get?key=$x"`
done

curl "http://localhost:50001/set?key=foo&value=blahfoo" | python -m json.tool 
curl "http://localhost:50001/set?key=boo&value=blahboo" | python -m json.tool 
curl "http://localhost:50001/set?key=goo&value=blahgoo" | python -m json.tool 
curl "http://localhost:50001/set?key=zoo&value=blahzoo" | python -m json.tool 