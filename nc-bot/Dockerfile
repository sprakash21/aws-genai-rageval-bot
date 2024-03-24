# nc-bot/Dockerfile
FROM python:3.9-slim
WORKDIR /app
RUN apt-get update && apt-get --no-install-recommends install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    tesseract-ocr libpoppler-dev libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*
COPY requirements_aws.txt /app/requirements_aws.txt
RUN pip3 install --no-cache-dir -r requirements_aws.txt
# All folders copy
COPY ./rag_application_framework /app/rag_application_framework
COPY ./pages /app/pages
# Remove this when on AWS. Should come from Secrets Manager,config and be read from it.
# COPY .env /app/.env
COPY chatbot.py /app/chatbot.py
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
ENTRYPOINT ["streamlit", "run", "chatbot.py", "--server.port=8501", "--server.address=0.0.0.0"]