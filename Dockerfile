FROM python:3.6-alpine3.8

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt&&pip install --no-cache https://github.com/learnforpractice/pyeoskit/releases/download/v0.3.0/pyeoskit-0.3.0-cp36-cp36m-linux_x86_64.whl

COPY diceminer.py ./diceminer.py

ENV NET "https://eos.greymass.com:443"
ENV INTERVAL 30
ENV ACCOUNT testtesttest
ENV AMOUNT 0.1
ENV TOKEN EOS
ENV ROLLMIN 2
ENV ROLLMAX 96
ENV PSW " "

CMD [ "python", "./diceminer.py" ]