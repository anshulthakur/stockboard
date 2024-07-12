FROM python:3.12
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app
COPY requirements.txt .
RUN apt update
RUN apt install build-essential wget -y
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
  tar -xvzf ta-lib-0.4.0-src.tar.gz && \
  cd ta-lib/ && \
  ./configure --prefix=/usr --build=aarch64-unknown-linux-gnu && \
  make && \
  make install
RUN pip3 install --no-cache-dir -r requirements.txt
