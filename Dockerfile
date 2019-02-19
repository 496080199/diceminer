FROM python:alpine3.8

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY diceminer.py ./diceminer.py

ENV NET "https://eos.greymass.com:443"
ENV INTERVAL 30
ENV ACCOUNT testtesttest
ENV AMOUNT 0.1
ENV TOKEN EOS
ENV ROLLMIN 2
ENV ROLLMAX 96

CMD [ "python", "./diceminer.py" ]