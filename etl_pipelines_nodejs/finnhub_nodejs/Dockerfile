FROM node:18-alpine3.18

# adding comment to test Github actions workflow

RUN mkdir -p /home/node/app/node_modules && chown -R node:node /home/node/app

WORKDIR /home/node/app

COPY package.json ./
COPY ./utils ./utils

USER node

RUN npm install && npm install typescript -g

COPY --chown=node:node ./src ./src

RUN tsc

CMD [ "node", "src/index.js" ]