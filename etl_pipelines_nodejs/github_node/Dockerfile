FROM node:19-alpine3.16

RUN mkdir -p /home/node/app/node_modules && chown -R node:node /home/node/app

WORKDIR /home/node/app

COPY package.json ./
COPY ./utils ./utils

USER node

RUN npm install

COPY --chown=node:node ./src ./src

EXPOSE 8080

CMD [ "node", "src/index.js" ]
