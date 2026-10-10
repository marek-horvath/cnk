FROM node:20-alpine AS frontend-deps

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

FROM frontend-deps AS frontend-dev

EXPOSE 8080

CMD ["npm", "run", "serve", "--", "--host", "0.0.0.0", "--port", "8080"]

FROM python:3.12-alpine AS api

WORKDIR /app/api

COPY api/ ./

ENV CNK_HOST=0.0.0.0 \
    CNK_PORT=3001 \
    CNK_DATA_DIR=/data \
    CNK_DB_PATH=/data/cnk.sqlite3 \
    PYTHONUNBUFFERED=1

EXPOSE 3001

CMD ["python", "cnk_api.py"]
