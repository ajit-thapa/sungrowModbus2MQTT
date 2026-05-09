FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY sungrow_modbus2mqtt/ ./sungrow_modbus2mqtt/

CMD ["python", "-m", "sungrow_modbus2mqtt.bridge", "-c", "config.yaml"]
