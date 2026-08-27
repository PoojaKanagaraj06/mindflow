FROM python:3.11-slim

WORKDIR /app

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy full project
COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
