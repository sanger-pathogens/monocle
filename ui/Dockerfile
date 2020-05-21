# ---------- build step ----------
FROM node:latest as builder

# label, so that intermediate images can easily be removed with
# `docker image prune --filter label=stage=builder`
LABEL stage=builder

# pass version at build time (displayed in footer)
ARG VERSION='VERSION'
ENV VERSION=$VERSION

# install (separation of COPY to help cache node_modules)
WORKDIR /app
COPY package.json yarn.lock /app/
RUN yarn install --silent --network-timeout 1000000
ENV PATH /app/node_modules/.bin:$PATH

# build the static files
COPY . /app
RUN yarn build


# ---------- production runtime ----------
FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
RUN chown -R nginx:nginx /usr/share/nginx/html/*
RUN chmod -R 0755 /usr/share/nginx/html/*
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
