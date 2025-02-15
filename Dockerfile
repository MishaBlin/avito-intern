FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
COPY pylintrc .

RUN pip install --no-cache-dir -r requirements.txt

COPY app .

EXPOSE 4000

CMD ["python", "-m", "flask", "--app", "api/main.py" ,"run", "--host=0.0.0.0", "--port=4000"]