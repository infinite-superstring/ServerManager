#/bin/bash 
#for loonginx-server

sudo yum -y update

sudo yum -y install docker-ce 

sudo systemctl enable docker

sudo systemctl start docker

sudo docker build -t loonginx-server ./

sudo docker run --name=loong -p 80:80 -v "$(pwd):/ServerManager-Panel" -itd loonginx-server
