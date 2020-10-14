# ---------- build step ----------
FROM node:alpine as builder

# label, so that intermediate images can easily be removed with
# `docker image prune --filter label=stage=builder`
LABEL stage=builder

# use the DOCKER_TAG build arg from hub.docker.com to set
# the version, or the string x.y.z as a default
ARG DOCKER_TAG=x.y.z

# install (separation of COPY to help cache node_modules)
WORKDIR /app
COPY package.json yarn.lock /app/
RUN yarn install --silent --network-timeout 1000000
ENV PATH /app/node_modules/.bin:$PATH

# copy source
COPY . /app

# build static files
RUN REACT_APP_VERSION=$DOCKER_TAG yarn build


# ---------- production runtime ----------
FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
RUN chown -R nginx:nginx /usr/share/nginx/html/*
RUN chmod -R 0755 /usr/share/nginx/html/*
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
