FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV BACKEND_PORT=8001

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir pydantic-settings

COPY config ./config
COPY src ./src
COPY web ./web
COPY data/knowledge_bases ./data/knowledge_bases
COPY .env.example ./.env.example

RUN mkdir -p \
    data/logs \
    data/homework_images \
    data/wrong_book \
    data/history \
    data/question_bank \
    data/user \
    data/user_profile

EXPOSE 8001

CMD ["python", "src/api/run_server.py"]
