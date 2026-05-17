#Stage 1

FROM python:3.11-alpine AS builder

WORKDIR /app

RUN apk add --no-cache gcc musl-dev libpq-dev

COPY requirements.txt .

RUN pip install --user --no-cache-dir -r requirements.txt

#Stage 

FROM python:3.11-alpine

WORKDIR /app


COPY --from=builder /root/.local /root/.local


COPY . .


ENV PATH=/root/.local/bin:$PATH

EXPOSE 3000

CMD ["python", "app.py"]
