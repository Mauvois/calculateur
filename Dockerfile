FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY calculateur.py .

EXPOSE 8501

CMD ["streamlit", "run", "calculateur.py", "--server.port=8501", "--server.enableCORS=false", "--server.headless=true"]
