FROM node:21.7.3 AS builder
WORKDIR /app

RUN npm install -g pnpm

COPY acc2/package.json acc2/pnpm-lock.yaml* ./

RUN pnpm install --include=dev

COPY acc2/ .

ARG VITE_BASE_API_URL

RUN echo "VITE_BASE_API_URL=${VITE_BASE_API_URL}" > .env.production

RUN pnpm build

FROM node:21.7.3-slim
WORKDIR /app

COPY --from=builder /app/dist ./dist

COPY acc2/package.json acc2/pnpm-lock.yaml* ./

RUN npm install -g pnpm serve

EXPOSE 3000

CMD ["pnpm", "prod"]
