
#!/bin/bash
ssh -t -i DiminishedTriad.pem ec2-user@52.26.45.12 "yes | sudo yum install git"
ssh -t -i DiminishedTriad.pem ec2-user@52.26.45.12 "mkdir dt"
ssh -t -i DiminishedTriad.pem ec2-user@52.26.45.12 "cd dt;git clone https://github.com/sanjeev87/DiminishedTriad.git"
ssh -t -i DiminishedTriad.pem ec2-user@52.26.45.12 "yes | sudo yum install python27-devel.x86_64"
ssh -t -i DiminishedTriad.pem ec2-user@52.26.45.12 "sudo pip install redis"    
ssh -t -i DiminishedTriad.pem ec2-user@52.26.45.12 "sudo pip install hiredis"  
ssh -t -i DiminishedTriad.pem ec2-user@52.26.45.12 "sudo pip install spyne"

