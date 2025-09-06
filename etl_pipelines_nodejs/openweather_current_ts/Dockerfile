# Build Stage
FROM node:22-alpine AS build

WORKDIR /app

COPY ./openweather_current_ts/package*.json ./
COPY ./openweather_current_ts/tsconfig.json ./
RUN npm ci

# Copy over source files
COPY ./openweather_current_ts ./openweather_current_ts
COPY ./openweather_current_ts/utils ./openweather_current_ts/utils
COPY ./openweather_current_ts/src ./openweather_current_ts/src
COPY ./common ./common

# Transpile
RUN npx tsc ./openweather_current_ts/src/index.ts

# Final Stage
FROM node:22-alpine AS production

WORKDIR /app

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copy over the production/final files
COPY --from=build /app/openweather_current_ts /app/openweather_current_ts
COPY --from=build /app/common /app/common
COPY --from=build /app/node_modules /app/node_modules

USER appuser
ENV NODE_ENV=production

CMD [ "node", "/app/openweather_current_ts/src/index.js" ]
