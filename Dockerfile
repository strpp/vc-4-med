FROM alpine
RUN apk update && apk add git python3 py3-pip
RUN git clone https://github.com/strpp/vc-4-med.git
WORKDIR /vc-4-med
RUN pip3 install -r requirements.txt
