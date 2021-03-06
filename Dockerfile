FROM node:14
WORKDIR /opt/DiscordTagsBot/
COPY package*.json ./
RUN npm install
COPY  . .
CMD [ "node", "index.js"]