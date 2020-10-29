# My application summary: #
![](https://i.imgur.com/m5OWuyI.png)
# Demo: #
(coming soon)
# Quick start: #
1. Setup environment for setting.py

	( Please Ctrl+F to search "How to setup environment for setting.py" )

2. Git clone this repo

        git clone https://github.com/kilbc634/discord_bot.git
3. Docker pull base image

		docker pull tuyn76801/ubuntu-18.04:200820
4. Copy SSL cert file to root directory for LINE bot part (can ignore this step when not need LINE bot application)

		bash cert_setup.sh
5. Build docker image with Dockerfile (may takes about 5 minutes)

		docker build -t tuyn76801/discord_bot .
6. Run docker container with parameters

		docker run -it -d \
		--name discord_bot \
		-e BOT_TOKEN=${BOT_TOKEN} \
		-e FB_ACCOUNT=${FB_ACCOUNT} \
		-e FB_PASSWORD=${FB_PASSWORD} \
		-e FB_NAME=${FB_NAME} \
		-e FB_GROUP=${FB_GROUP} \
		-e REDIS_HOST=${REDIS_HOST}
		-e REDIS_AUTH=${REDIS_AUTH} \
		-e API_HOST=${API_HOST} \
		-e LINE_SECRET=${LINE_SECRET} \
		-e LINE_TOKEN=${LINE_TOKEN} \
		-p 21090:21090 \
		-p 21190:21190 \
		-p 443:443 \
		-p 80:80 \
		tuyn76801/discord_bot

# How to setup environment for setting.py: #

----------

- ${BOT_TOKEN}

(1) Create a discord bot application from Discord Developer Portal([https://discord.com/developers/applications](https://discord.com/developers/applications))

(2) Invite bot to specific discord server, and give bot required permissions

(3) Set ${BOT_TOKEN} of env variable is bot TOKEN

----------

- ${FB_ACCOUNT}, ${FB_PASSWORD}, ${FB_NAME}, ${FB_GROUP}

(1) Create a FaceBook account with ${FB_ACCOUNT} and ${FB_PASSWORD} (this account same as normal account, no need more setting for bot)

(2) And this account full name should be ${FB_NAME}

(3) Invite this account to a group called ${FB_GROUP}

(4) Set ${FB_ACCOUNT}, ${FB_PASSWORD}, ${FB_NAME}, ${FB_GROUP} for env variable

----------

- ${REDIS_HOST}, ${REDIS_AUTH}

(1) Run Redis server in ${REDIS_HOST}(port 6379), and set auth password is ${REDIS_AUTH}

(2) Set ${REDIS_HOST}, ${REDIS_AUTH} for env variable

----------

- ${API_HOST}

(1) Set ${API_HOST} of env variable is you self host:21090

(2) You can set ${API_HOST} is "http://127.0.0.1:21090" if running local

----------

- ${LINE_SECRET}, ${LINE_TOKEN} **(Optional)**

(1) Create a LINE bot application from LINE Developers([https://developers.line.biz/](https://developers.line.biz/))

(2) Invite bot to specific group chat room

(3) Set ${LINE_SECRET}, ${LINE_TOKEN}

----------

