FROM continuumio/miniconda3:4.10.3
MAINTAINER Mingxun Wang "mwang87@gmail.com"

COPY requirements.txt . 
COPY requirements_unique.txt . 
RUN pip install -r requirements.txt
RUN pip install -r requirements_unique.txt
RUN pip install -U Celery
RUN pip install git+https://github.com/Wang-Bioinformatics-Lab/GNPSDataPackage.git
 
# install mamba
#RUN conda install -c conda-forge mamba

# Install nextflow as a new env
#RUN mamba create -n nextflow -c conda-forge -c bioconda nextflow==21.10.0

COPY . /app
WORKDIR /app
