FROM node:18-alpine3.18

WORKDIR /app

COPY ./openweather_current_ts/package*.json ./
COPY ./openweather_current_ts/tsconfig.json ./

RUN npm ci

COPY ./openweather_current_ts ./openweather_current_ts
COPY ./openweather_current_ts/utils ./openweather_current_ts/utils
COPY ./openweather_current_ts/src ./openweather_current_ts/src
COPY ./common ./common 

RUN npx tsc ./openweather_current_ts/src/src/index.ts

CMD [ "node", "/app/openweather_current_ts/src/index.js" ]