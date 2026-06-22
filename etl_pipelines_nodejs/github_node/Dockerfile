# Build Stage
FROM node:22-bookworm-slim AS build

WORKDIR /app

COPY ./github_node/package*.json ./
COPY ./github_node/tsconfig.json ./
RUN npm ci

# Copy source files
COPY ./github_node ./github_node
COPY ./common ./common

# Transpile
RUN npx tsc ./github_node/src/index.ts

# Final Stage
FROM node:22-bookworm-slim AS production

WORKDIR /app

ENV NODE_ENV=production

# Copy over the production/final files
COPY --from=build /app/github_node /app/github_node
COPY --from=build /app/common /app/common
COPY --from=build /app/node_modules /app/node_modules

USER node

CMD ["node", "/app/github_node/src/index.js"]

