# Build Stage
FROM node:22-bookworm-slim AS build

WORKDIR /app

COPY ./finnhub_nodejs/package*.json ./finnhub_nodejs/tsconfig.json ./
RUN npm ci

COPY ./finnhub_nodejs ./finnhub_nodejs
COPY ./common ./common

RUN npx tsc ./finnhub_nodejs/src/index.ts
RUN npm prune --omit=dev

# Final Stage
FROM node:22-bookworm-slim AS production

WORKDIR /app

ENV NODE_ENV=production

COPY --from=build /app/finnhub_nodejs /app/finnhub_nodejs
COPY --from=build /app/common /app/common
COPY --from=build /app/node_modules /app/node_modules

USER node

CMD ["node", "/app/finnhub_nodejs/src/index.js"]
