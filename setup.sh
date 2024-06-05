#/bin/bash 
#for loonginx-server

sudo yun -y update

sudo yum install docker-ce 

sudo systemctl enable docker

sudo docker build -t loonginx-server1.0 ./

sudo docker run --name=loong -p 80:80 -v /ServerManager-Panel:/ServerManager-Panel -itd loonginx-server1.0
