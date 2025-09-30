# app/Dockerfile
FROM python:3.11-slim

# install system deps and a minimal texlive set with pdflatex
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    wget \
    git \
    unzip \
    poppler-utils \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-xetex \
    fonts-dejavu-core \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# working directory
WORKDIR /app

# copy repo files (only what the app needs)
COPY ./app /app
COPY ./utils /app/utils
COPY ./tailor_resume.py /app/tailor_resume.py
COPY ./requirements.txt /app/requirements.txt

# install python deps
RUN pip install --no-cache-dir -r /app/requirements.txt

# expose port
EXPOSE 8000

# uvicorn startup
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
