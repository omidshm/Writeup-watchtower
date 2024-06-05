FROM python:3.11-slim

ADD . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "bot.py"]