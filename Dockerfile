FROM debian:bullseye-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    iproute2 \
    python3 \
    python3-pip \
    curl \
 && rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["python3", "main.py"]
