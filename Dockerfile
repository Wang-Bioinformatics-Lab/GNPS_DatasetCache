FROM continuumio/miniconda3:4.10.3
MAINTAINER Mingxun Wang "mwang87@gmail.com"

COPY requirements.txt . 
COPY requirements_unique.txt . 
RUN pip install -r requirements.txt
RUN pip install -r requirements_unique.txt
RUN pip install -U Celery
RUN pip install git+https://github.com/Wang-Bioinformatics-Lab/GNPSDataPackage.git

COPY . /app
WORKDIR /app
