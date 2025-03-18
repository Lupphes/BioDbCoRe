# Stage 1: Build dependencies
FROM python:3.12 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -t /app/packages

# Stage 2: Create the final container
FROM nfcore/base:3.12
WORKDIR /app
COPY --from=builder /app/packages /app/packages
COPY downloader_pipeline/ /app/downloader_pipeline/
COPY main.py /app/main.py
RUN chmod +x /app/main.py

ENV PYTHONPATH="/app/packages:$PYTHONPATH"