FROM python

WORKDIR /app

RUN mkdir pipeline

COPY requirements.txt ./pipeline

RUN pip3 install -r ./pipeline/requirements.txt

COPY extract.py ./pipeline

COPY transform.py ./pipeline

COPY load.py ./pipeline

COPY pipeline.py ./pipeline

CMD python3 ./pipeline/pipeline.py