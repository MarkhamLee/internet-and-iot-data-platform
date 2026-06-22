# Build Stage
FROM node:22-bookworm-slim AS build

WORKDIR /app

COPY ./openweather_airquality_nodejs/package*.json ./
COPY ./openweather_airquality_nodejs/tsconfig.json ./
RUN npm ci

# Copy source files
COPY ./openweather_airquality_nodejs ./openweather_airquality_nodejs
COPY ./common ./common

# Transpile into JavaScript
RUN npx tsc ./openweather_airquality_nodejs/src/index.ts

# Final Stage
FROM node:22-bookworm-slim AS production

WORKDIR /app

ENV NODE_ENV=production

# Copy over the production/final files
COPY --from=build /app/openweather_airquality_nodejs /app/openweather_airquality_nodejs
COPY --from=build /app/common /app/common
COPY --from=build /app/node_modules /app/node_modules

USER node

CMD ["node", "/app/openweather_airquality_nodejs/src/index.js"]