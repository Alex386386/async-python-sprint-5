FROM python:3.8-slim
WORKDIR /app
COPY . .
RUN apt-get update \
    && apt-get install -y netcat-openbsd \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install -r requirements.txt --no-cache-dir \
    && chmod +x /app/entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]