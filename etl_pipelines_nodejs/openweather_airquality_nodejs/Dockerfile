# Build Stage
FROM node:22-alpine AS build

WORKDIR /app

COPY ./openweather_airquality_nodejs/package*.json ./
COPY ./openweather_airquality_nodejs/tsconfig.json ./
RUN npm ci

# Copy over source files
COPY ./openweather_airquality_nodejs ./openweather_airquality_nodejs
COPY ./openweather_airquality_nodejs/utils ./openweather_airquality_nodejs/utils
COPY ./openweather_airquality_nodejs/src ./openweather_airquality_nodejs/src
COPY ./common ./common

# Transpile
RUN npx tsc ./openweather_airquality_nodejs/src/index.ts

# Final Stage
FROM node:22-alpine AS production

WORKDIR /app

# Copy over the production/final files
COPY --from=build /app/openweather_airquality_nodejs /app/openweather_airquality_nodejs
COPY --from=build /app/common /app/common

CMD [ "node", "/app/openweather_airquality_nodejs/src/index.js" ]

