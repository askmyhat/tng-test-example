FROM python:3.6-onbuild
MAINTAINER askhat.nuriddinov@ugent.be

RUN     apt-get update && apt-get install -y \
        net-tools \
        iproute \
        inetutils-ping \
        curl

ENV SON_EMU_CMD "echo Python VNF tester is ready"

CMD /bin/bash
