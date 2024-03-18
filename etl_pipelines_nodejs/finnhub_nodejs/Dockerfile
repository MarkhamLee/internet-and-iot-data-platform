FROM node:18-alpine3.18

WORKDIR /app

COPY ./finnhub_nodejs/package*.json ./
COPY ./finnhub_nodejs/tsconfig.json ./

RUN npm ci

COPY ./finnhub_nodejs ./finnhub_nodejs
COPY ./finnhub_nodejs/src ./finnhub_nodejs/src
COPY ./finnhub_nodejs/utils ./finnhub_nodejs/utils

COPY ./common ./common 

RUN npx tsc ./finnhub_nodejs/src/index.ts

CMD [ "node", "/finnhub_nodejs/src/index.js" ]