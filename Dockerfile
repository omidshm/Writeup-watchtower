FROM python:3.11-slim

ADD bot.py .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "bot.py"]