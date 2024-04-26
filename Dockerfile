FROM python:3.11

RUN mkdir /solana_tokens_app

WORKDIR /solana_tokens_app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

CMD python3 main.py
