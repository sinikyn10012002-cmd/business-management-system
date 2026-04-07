FROM python:3.12-slim

WORKDIR /project

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /project/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/project/entrypoint.sh"]