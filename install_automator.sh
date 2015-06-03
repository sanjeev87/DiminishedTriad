
#declare -a arr=("ec2-52-26-45-12.us-west-2.compute.amazonaws.com" "ec2-52-10-168-27.us-west-2.compute.amazonaws.com" "ec2-52-24-138-59.us-west-2.compute.amazonaws.com" "ec2-52-24-228-62.us-west-2.compute.amazonaws.com" "ec2-52-25-225-154.us-west-2.compute.amazonaws.com" "ec2-52-25-235-10.us-west-2.compute.amazonaws.com" "ec2-52-26-12-148.us-west-2.compute.amazonaws.com" "ec2-52-26-48-223.us-west-2.compute.amazonaws.com")
declare -a arr=("ec2-52-24-47-158.us-west-2.compute.amazonaws.com")
# declare -a arr=("ec2-52-26-45-12.us-west-2.compute.amazonaws.com")
for i in "${arr[@]}"
do
   echo "Installing on: $i"
    # ssh -t -i DiminishedTriad.pem ec2-user@${i} "sudo pip install --upgrade pip"
    # ssh -t -i DiminishedTriad.pem ec2-user@${i} "cp /usr/local/bin/pip /usr/bin"
    ssh -t -i DiminishedTriad.pem ec2-user@${i} "yes | sudo yum install gcc"
    ssh -t -i DiminishedTriad.pem ec2-user@${i} "yes | sudo yum install git"
    ssh -t -i DiminishedTriad.pem ec2-user@${i} "mkdir dt"
    ssh -t -i DiminishedTriad.pem ec2-user@${i} "cd dt;git clone https://github.com/sanjeev87/DiminishedTriad.git"
    ssh -t -i DiminishedTriad.pem ec2-user@${i} "yes | sudo yum install python27-devel.x86_64"
    ssh -t -i DiminishedTriad.pem ec2-user@${i} "sudo pip install redis"    
    ssh -t -i DiminishedTriad.pem ec2-user@${i} "sudo pip install hiredis"  
    ssh -t -i DiminishedTriad.pem ec2-user@${i} "sudo pip install spyne"
done
