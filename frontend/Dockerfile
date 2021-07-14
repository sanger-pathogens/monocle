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

WORKDIR /app
COPY --from=builder /app .
COPY . .

EXPOSE 3000
CMD ["node", "./build"]

