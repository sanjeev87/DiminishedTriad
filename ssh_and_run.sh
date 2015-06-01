#!/bin/bash
USERNAME=mmoharan
VM_S=143
VM_END=152



if [ "$1" == "p" ]; then
    USERNAME=p1agarwa
fi

if [ "$1" == "s" ]; then
    USERNAME=sajagann
fi

if [ "$1" == "m" ]; then
    USERNAME=mmoharan
fi

if [ "$2" == "all" ]; then
    I=$VM_S
    for ((I=$VM_S; I <= $VM_END; I++))
    do
        ssh cse223_${USERNAME}@vm${I}.sysnet.ucsd.edu "bash -s" < remotecmd.sh  
    done
else
    ssh cse223_${USERNAME}@vm148.sysnet.ucsd.edu "bash -s" < remotecmd.sh  
fi



# whoami
# pwd
