#/bin/bash 
#for loonginx-server

sudo yum -y update

sudo yum -y install docker-ce 

sudo systemctl enable docker

sudo systemctl start docker

sudo docker build -t loonginx-server1.0 ./

sudo docker run --name=loong -p 80:80 -v /ServerManager-Panel:/ServerManager-Panel -itd loonginx-server1.0
