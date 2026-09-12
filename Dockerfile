# Introduction to Big Data - lab environment, Ubuntu 24.04
#   docker build -t bigdata-lab .
#   docker run -it --rm -v "$PWD:/work" bigdata-lab bash
FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive TZ=Asia/Seoul
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 python3-pip python3-venv openjdk-17-jre-headless \
      curl wget unzip git ca-certificates procps time less \
 && rm -rf /var/lib/apt/lists/*
# Ubuntu 24.04 blocks system-wide pip, so we use a virtualenv (PEP 668)
RUN python3 -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt
WORKDIR /work
CMD ["bash"]
