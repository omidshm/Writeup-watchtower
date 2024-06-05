FROM python:3.11-slim

ADD . .

RUN pip install --no-cache-dir -r requirements.txt

ENV PATH=$PATH:.

CMD ["python", "bot.py"]