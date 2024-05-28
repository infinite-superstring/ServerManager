FROM cr.loongnix.cn/library/debian:buster

LABEL maintainer="fsj,yf"

EXPOSE 80

RUN apt-get update && \
    apt-get install -y wget git unzip build-essential gdb lcov pkg-config \
    libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev liblzma-dev \
    libncurses5-dev libreadline6-dev libsqlite3-dev libssl-dev \
    lzma lzma-dev tk-dev uuid-dev zlib1g-dev libmpdec-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir ServerManager-Panel

COPY . /ServerManager-Panel

WORKDIR /ServerManager-Panel

RUN wget http://ftp.loongnix.cn/toolchain/rust/rust-1.78/2024-05-06/abi1.0/rust-1.78.0-loongarch64-unknown-linux-gnu.tar.gz

RUN tar zxf rust-1.78.0-loongarch64-unknown-linux-gnu.tar.gz

RUN ./rust-1.78.0-loongarch64-unknown-linux-gnu/install.sh

ARG ARCH
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        apt-get update && apt-get install -y python3.10 python3.10-venv python3.10-dev && \
        apt-get clean && rm -rf /var/lib/apt/lists/*; \
    elif [ "$ARCH" = "loongarch64" ]; then \
        wget https://github.com/loongarch64/cpython/archive/refs/tags/v3.10.2.zip && \
        unzip v3.10.2.zip && \
        cd cpython-3.10.2 && \
        ./configure && \
        make && \
        make install && \
        cd .. && \
        rm -rf cpython-3.10.2 v3.10.2.zip; \
    else \
        echo "Unsupported architecture" && exit 1; \
    fi

RUN pip3 install -r ./requirements.txt && \
    python3 manage.py makemigrations && \
    python3 manage.py migrate && \
    python3 manage.py initial_data

CMD ["python3", "manage.py", "runserver", "127.0.0.1:80"]
