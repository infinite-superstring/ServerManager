FROM debian:latest
LABEL authors="fsj"

RUN apt update
RUN apt-get install wget git build-essential gdb lcov pkg-config \
      libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev liblzma-dev \
      libncurses5-dev libreadline6-dev libsqlite3-dev libssl-dev \
      lzma lzma-dev tk-dev uuid-dev zlib1g-dev libmpdec-dev \

RUN mkdir build
RUN mkdir build/Scripts
RUN cd build
COPY bash/build-cpython.sh ~/build/Scripts

RUN ./build/Scripts/build-cpython.sh

COPY

#ENTRYPOINT ["top", "-b"]