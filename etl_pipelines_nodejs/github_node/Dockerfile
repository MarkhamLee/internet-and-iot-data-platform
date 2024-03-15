FROM node:18-alpine3.18

WORKDIR /app

COPY package*.json ./
COPY tsconfig.json ./

RUN npm ci


COPY ./utils ./utils
COPY ./src ./src

RUN npx tsc ./src/index.ts

CMD [ "node", "src/index.js" ]
