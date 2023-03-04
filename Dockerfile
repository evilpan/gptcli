FROM alpine:latest

COPY . /gptcli

RUN apk update

RUN apk add --no-cache python3 python3-dev py3-pip build-base && \
    pip3 install --no-cache-dir -r /gptcli/requirements.txt

WORKDIR /gptcli

ENTRYPOINT ["python3", "-u", "gptcli.py"]