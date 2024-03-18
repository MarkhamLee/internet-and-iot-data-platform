FROM node:18-alpine3.18

WORKDIR /app

COPY ./openweather_airquality_nodejs/package*.json ./
COPY ./openweather_airquality_nodejs/tsconfig.json ./

RUN npm ci

COPY ./openweather_airquality_nodejs ./openweather_airquality_nodejs
COPY ./openweather_airquality_nodejs/utils ./openweather_airquality_nodejs/utils
COPY ./openweather_airquality_nodejs/src ./openweather_airquality_nodejs/src
COPY ./common ./common 

RUN npx tsc ./openweather_airquality_nodejs/src/index.ts

CMD [ "node", "/app/openweather_airquality_nodejs/src/index.js" ]