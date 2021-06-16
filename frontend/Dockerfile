# ---------- build step ----------
FROM gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle/node:alpine as builder

WORKDIR /app
COPY package.json package-lock.json /app/
RUN npm set audit false &&\
  npm config set fetch-timeout 1000000 &&\
  npm install --silent
ENV PATH /app/node_modules/.bin:$PATH

# copy source, config, & asset files
COPY . /app

# build production bundle
RUN npm run build


# ---------- production runtime ----------
FROM gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/monocle/nginx:alpine
COPY --from=builder /app/public /usr/share/nginx/html
RUN chown -R nginx:nginx /usr/share/nginx/html/*
RUN chmod -R 0755 /usr/share/nginx/html/*
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

