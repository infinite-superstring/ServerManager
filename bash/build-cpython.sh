#!/bin/bash

# 检查当前架构
ARCH=$(uname -m)
loongarch64_python_vresion = 3.10.2


# 根据架构选择不同的 GitHub 仓库
if [ "$ARCH" == "x86_64" ]; then
    apt install python3.10 python3.10-venv python3.10-dev
elif [ "$ARCH" == "loongarch64" ]; then
    wget https://github.com/loongarch64/cpython/archive/refs/tags/v{$loongarch64_python_vresion}.zip
    cd cpyton-{$loongarch64_python_vresion}
    ./configure
    make
    make install
else
    echo "Unsupported architecture"
    exit 1
fi