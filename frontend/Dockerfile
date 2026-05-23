ARG DOCKER_REGISTRY=docker.arvancloud.ir
ARG DOCKER_OFFICIAL_NAMESPACE=library
FROM ${DOCKER_REGISTRY}/${DOCKER_OFFICIAL_NAMESPACE}/node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
ARG NPM_REGISTRY=https://npm.devneeds.ir/
RUN npm config set registry "${NPM_REGISTRY}" && npm install

FROM ${DOCKER_REGISTRY}/${DOCKER_OFFICIAL_NAMESPACE}/node:20-alpine AS runner
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]
