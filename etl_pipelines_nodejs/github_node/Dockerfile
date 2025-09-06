# Build Stage
FROM node:22-alpine AS build

WORKDIR /app

COPY ./github_node/package*.json ./
COPY ./github_node/tsconfig.json ./
RUN npm ci

# Copy over source files
COPY ./github_node ./github_node
COPY ./github_node/utils ./github_node/utils
COPY ./github_node/src ./github_node/src
COPY ./common ./common

# Transpile
RUN npx tsc ./github_node/src/index.ts

# Final Stage
FROM node:22-alpine AS production

WORKDIR /app

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copy over the production/final files
COPY --from=build /app/github_node /app/github_node
COPY --from=build /app/common /app/common

USER appuser
ENV NODE_ENV=production

CMD [ "node", "/app/github_node/src/index.js" ]

