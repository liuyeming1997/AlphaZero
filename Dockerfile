
FROM python:3.8

RUN mkdir AlphaZero
COPY . AlphaZero
RUN pip install -r ./AlphaZero/requirements.txt
WORKDIR ./AlphaZero/
CMD python3 main.py
