# Build Stage
FROM node:22-bookworm-slim AS build

WORKDIR /app

COPY ./openweather_current_ts/package*.json ./
COPY ./openweather_current_ts/tsconfig.json ./
RUN npm ci

# Copy over source files
COPY ./openweather_current_ts ./openweather_current_ts
COPY ./common ./common

# Transpile
RUN npx tsc ./openweather_current_ts/src/index.ts

# Final Stage
FROM node:22-bookworm-slim AS production

WORKDIR /app

ENV NODE_ENV=production

# Copy over the production/final files
COPY --from=build /app/openweather_current_ts /app/openweather_current_ts
COPY --from=build /app/common /app/common
COPY --from=build /app/node_modules /app/node_modules

USER node

CMD ["node", "/app/openweather_current_ts/src/index.js"]
