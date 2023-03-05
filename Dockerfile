FROM python:3.11-alpine

COPY . /gptcli

WORKDIR /gptcli

RUN python3 -m pip install -i https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir -r /gptcli/requirements.txt

ENTRYPOINT ["python3", "-u", "gptcli.py"]