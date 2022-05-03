# ---------- build step ----------
FROM gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle/node:16.4.2-alpine3.14 as builder

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm set audit false &&\
  npm config set fetch-timeout 1000000 &&\
  npm install --silent

# copy source, config, & asset files
COPY . .

# build production bundle
RUN npm run build

# ---------- production runtime ----------
FROM gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle/node:16.4.2-alpine3.14

ENV NODE_ENV=production
WORKDIR /app
COPY --from=builder /app .
COPY . .

# cache bust to update quickly the image build time
# pass a new value as CACHE_BUST, e.g. with `--build-arg "CACHE_BUST=$(date)"`
ARG      CACHE_BUST
RUN      echo "$CACHE_BUST" > /dev/null

EXPOSE 3000
CMD ["node", "./build"]

