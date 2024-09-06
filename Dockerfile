    FROM python:3.13.0rc1-slim-bookworm

    WORKDIR /app

    COPY requirements.txt requirements.txt
    RUN pip install --no-cache-dir -r requirements.txt

    COPY . .

    EXPOSE 5000


    CMD ["python3", "app.py"]
