FROM ubuntu:22.04
MAINTAINER Mingxun Wang "mwang87@gmail.com"

RUN apt-get update && apt-get install -y build-essential libarchive-dev wget vim

# Install Mamba
ENV CONDA_DIR /opt/conda
RUN wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh -O ~/miniforge.sh && /bin/bash ~/miniforge.sh -b -p /opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH

# Adding to bashrc
RUN echo "export PATH=$CONDA_DIR:$PATH" >> ~/.bashrc

COPY requirements.txt . 
COPY requirements_unique.txt . 
RUN pip install -r requirements.txt
RUN pip install -r requirements_unique.txt
RUN pip install -U Celery

RUN apt-get update && apt-get install -y git
RUN pip install git+https://github.com/Wang-Bioinformatics-Lab/GNPSDataPackage.git
RUN pip install python-dotenv

# Install nextflow in the base env
RUN conda install -c bioconda nextflow

COPY . /app
WORKDIR /app
