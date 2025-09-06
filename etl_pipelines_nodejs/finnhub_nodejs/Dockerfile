# Build Stage
FROM node:22-alpine AS build

WORKDIR /app

COPY ./finnhub_nodejs/package*.json ./
COPY ./finnhub_nodejs/tsconfig.json ./
RUN npm ci

# Copy over source files 
COPY ./finnhub_nodejs ./finnhub_nodejs
COPY ./finnhub_nodejs/src ./finnhub_nodejs/src
COPY ./finnhub_nodejs/utils ./finnhub_nodejs/utils
COPY ./common ./common

# Transpile the files into JavaScript
RUN npx tsc ./finnhub_nodejs/src/index.ts

# Final Stage
FROM node:22-alpine AS production

WORKDIR /app

# Copy over the production/final files 
COPY --from=build /app/finnhub_nodejs /app/finnhub_nodejs
COPY --from=build /app/common /app/common

CMD [ "node", "/app/finnhub_nodejs/src/index.js" ]
