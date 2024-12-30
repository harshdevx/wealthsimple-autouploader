FROM python:3

COPY ./src /src
WORKDIR /src
COPY requirements.txt ./
RUN pip3 install -r requirements.txt
CMD [ "python", "main.py"]
