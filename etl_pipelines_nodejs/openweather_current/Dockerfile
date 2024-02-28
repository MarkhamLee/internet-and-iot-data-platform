# FROM node:10-alpine

FROM node:19-alpine3.16

RUN mkdir -p /home/node/app/node_modules && chown -R node:node /home/node/app

WORKDIR /home/node/app

COPY package.json ./

USER node

RUN npm install

COPY --chown=node:node index.js .

EXPOSE 8080

CMD [ "node", "index.js" ]