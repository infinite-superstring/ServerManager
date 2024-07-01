#/bin/bash 
#for loonginx-server

sudo yum -y update

sudo yum -y install docker-ce 

sudo systemctl enable docker

sudo systemctl start docker

sudo docker build -t loonginx-server ./

sudo mkdir /ServerManager-Panel

sudo mv . /ServerManager-Panel

sudo docker run --name=loong -p 80:80 -v /ServerManager-Panel:/ServerManager-Panel -itd loonginx-server
