FROM node:21.7.3 AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml* ./
COPY . .
RUN npm install -g pnpm && pnpm install --include=dev && pnpm build

FROM node:21.7.3-slim
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY package.json pnpm-lock.yaml* ./
RUN npm install -g pnpm serve
EXPOSE 3000
CMD ["pnpm", "prod"]
