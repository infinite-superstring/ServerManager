#!/usr/bin/env bash

# 检测系统发行版
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
    else
        echo "Unsupported OS"
        exit 1
    fi
}

# 安装 Docker 和 Docker Compose
install_docker() {
    case "$OS" in
        ubuntu|debian)
            sudo apt-get update
            sudo apt-get install -y \
                apt-transport-https \
                ca-certificates \
                curl \
                gnupg \
                lsb-release
            curl -fsSL https://download.docker.com/linux/$OS/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
            echo \
                "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/$OS \
                $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            sudo apt-get update
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io
            ;;
        centos|fedora|rhel)
            sudo yum install -y yum-utils
            sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            sudo yum install -y docker-ce docker-ce-cli containerd.io
            ;;
        *)
            echo "Unsupported OS"
            exit 1
            ;;
    esac

    sudo systemctl start docker
    sudo systemctl enable docker

    # 安装 Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.28.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
}

# 运行 Docker Compose
run_docker_compose() {
    if [ -f docker-compose.x86.yml ]; then
        docker-compose -f docker-compose.x86.yml up -d
    else
        echo "docker-compose.yml not found"
        exit 1
    fi
}

ARCH=$(uname -m)

if [ "$ARCH" = "x86_64" ]; then
    detect_os
    install_docker
    run_docker_compose
elif [ "$ARCH" = "loongarch64" ]; then
    yum install wget git
    # 安装 docker ce
    tar -xf ./installer/loongarch64/docker-27.0.3.tgz -C /usr/local/bin/
    cp ./installer/loongarch64/docker.service /etc/systemd/system/docker.service
    systemctl daemon-reload
    systemctl start docker
    systemctl enable docker
    # 安装 docker compose
    cp ./installer/loongarch64/docker-compose-linux-loongarch64 /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    # 运行docker
    docker-compose -f docker-compose.loongarch.yml up -d
    # 清理
    rm -rf docker
else
    echo "不支持的系统架构: ${ARCH}" && exit 1;
fi