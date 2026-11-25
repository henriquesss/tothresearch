# Build context: the repository root (the web app needs the pnpm workspace).
FROM node:22-slim

RUN corepack enable

WORKDIR /repo

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/web/package.json apps/web/
COPY packages/shared/package.json packages/shared/
RUN pnpm install --frozen-lockfile --filter @toth/web...

COPY packages/shared packages/shared
COPY apps/web apps/web

WORKDIR /repo/apps/web
EXPOSE 5173

CMD ["pnpm", "exec", "vite", "--host", "0.0.0.0", "--port", "5173"]
