FROM python:3.11-slim

WORKDIR /usr/src/app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV NAME BOT_TOKEN
ENV NAME CHAT_ID

CMD ["python", "bot.py"]