FROM node:18-alpine3.18

WORKDIR /app

COPY ./finnhub_nodejs/package*.json ./
COPY ./finnhub_nodejs/tsconfig.json ./

RUN npm ci

COPY ./finnhub_nodejs/ ./finnhub_nodejs/
COPY ./common/ ./common/

RUN npx tsc ./src/index.ts

CMD [ "node", "src/index.js" ]