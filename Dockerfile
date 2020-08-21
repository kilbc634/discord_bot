FROM tuyn76801/ubuntu-18.04:200820
ENV APP_NAME="discord_bot"
WORKDIR /home

RUN mkdir ${APP_NAME}
RUN cd ${APP_NAME}
ADD ./ ./

RUN pip3 install -r requirements.txt

EXPOSE 21090
CMD ["python3", "discord_bot.py"]