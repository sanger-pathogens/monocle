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


FROM gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle

WORKDIR /app
COPY --from=0 /app .
COPY . .

EXPOSE 80
CMD ["node", "./build"]

