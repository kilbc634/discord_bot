FROM tuyn76801/ubuntu-18.04:200820
ENV APP_NAME="discord_bot"
WORKDIR /home/${APP_NAME}

EXPOSE 21090

ADD ./ ./
RUN pip3 install -r requirements.txt

CMD python3 discord_bot.py