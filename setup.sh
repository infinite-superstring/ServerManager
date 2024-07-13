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
    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
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
    wget https://github.com/wojiushixiaobai/docker-ce-binaries-loongarch64/releases/download/v27.0.3/docker-27.0.3.tgz
    tar -xf docker-27.0.3.tgz
    cp docker/* /usr/local/bin/
    wget https://raw.githubusercontent.com/jumpserver/installer/master/scripts/docker.service -O /etc/systemd/system/docker.service
    systemctl start docker
    # 安装 docker compose
    wget -O /usr/libexec/docker/cli-plugins/docker-compose https://github.com/wojiushixiaobai/compose-loongarch64/releases/download/v2.28.1/docker-compose-linux-loongarch64
    chmod +x /usr/libexec/docker/cli-plugins/docker-compose
    # 安装 buildx
    wget -O /usr/libexec/docker/cli-plugins/docker-buildx https://github.com/wojiushixiaobai/buildx-loongarch64/releases/download/v0.16.0/buildx-v0.16.0-linux-loongarch64
    chmod +x /usr/libexec/docker/cli-plugins/docker-buildx
    # 运行docker
    docker-compose -f docker-compose.loongarch.yml up -d
else
    echo "不支持的系统架构: ${ARCH}" && exit 1;
fi