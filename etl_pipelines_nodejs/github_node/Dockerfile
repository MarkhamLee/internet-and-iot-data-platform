FROM node:18-alpine3.18

WORKDIR /app

COPY ./github_node/package*.json ./
COPY ./github_node/tsconfig.json ./

RUN npm ci

COPY ./github_node ./github_node
COPY ./github_node/utils ./github_node/utils
COPY ./github_node/src ./github_node/src
COPY ./common ./common 

RUN npx tsc ./github_node/src/index.ts

CMD [ "node", "/app/github_node/src/index.js" ]
