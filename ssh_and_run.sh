#!/bin/bash
USERNAME=cse223_mmoharan
VM_S=143
VM_END=152


if [ "$1" == "all" ]; then
    I=$VM_S
    for ((I=$VM_S; I <= $VM_END; I++))
    do
        ssh ${USERNAME}@vm${I}.sysnet.ucsd.edu "bash -s" < remotecmd.sh  
    done
else
    ssh ${USERNAME}@vm148.sysnet.ucsd.edu "bash -s" < remotecmd.sh  
fi

# whoami
# pwd
