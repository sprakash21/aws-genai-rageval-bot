# nc-bot/Dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get --no-install-recommends install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    tesseract-ocr libpoppler-dev libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/* && apt-get clean
RUN useradd -ms /bin/bash app
WORKDIR /home/app
COPY requirements_aws.txt /home/app/requirements_aws.txt
RUN pip3 install --no-cache-dir -r requirements_aws.txt
# All folders copy
USER app
COPY ./rag_application_framework /home/app/rag_application_framework
COPY requests /home/app/pages
# Remove this when on AWS. Should come from Secrets Manager,config and be read from it.
#COPY .env /home/app/.env
COPY app.py /home/app/chatbot.py
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
ENTRYPOINT ["streamlit", "run", "chatbot.py", "--server.port=8501", "--server.address=0.0.0.0"]