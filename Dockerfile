FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python src/generate_samples.py && \
    python -c "import torch; from src.classifier import MobileNetV3Waste; torch.save(MobileNetV3Waste(6).state_dict(), 'models/waste_classifier.pt')"

EXPOSE 8011

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8011"]
