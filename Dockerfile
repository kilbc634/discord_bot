FROM tuyn76801/ubuntu-18.04:200820
ENV APP_NAME="discord_bot"
ENV LANG="C.UTF-8"
# install Chinese fonts for FaceBook web page
RUN apt install -y fonts-wqy-*
RUN fc-cache -f -v
WORKDIR /home/${APP_NAME}

EXPOSE 21090
EXPOSE 21190
EXPOSE 443
EXPOSE 80

ADD ./ ./
RUN pip3 install --no-cache-dir -r requirements.txt
# install chrome
RUN apt update
RUN apt install -y unzip openjdk-8-jre-headless xvfb libxi6 libgconf-2-4
RUN apt install -y curl
RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add
RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
RUN apt -y update
RUN apt -y install google-chrome-stable
RUN apt -y install ffmpeg
# download webdevice for linux
RUN CHROMEDRIVER_VERSION=$(curl -sS https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE) && \
    wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" -O /tmp/chromedriver.zip
RUN unzip /tmp/chromedriver.zip -d /tmp
RUN mv /tmp/chromedriver /tmp/chromedriver_linux
RUN mv /tmp/chromedriver_linux lib/
RUN rm /tmp/chromedriver.zip

# change webdevice permission
RUN chmod 777 lib/chromedriver_linux
RUN chmod 777 lib/chromedriver_win.exe

CMD python3 discord_bot.py
