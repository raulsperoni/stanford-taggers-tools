FROM node:argon

# Create app directory
RUN mkdir -p /usr/src/krypton
WORKDIR /usr/src/krypton
COPY . /usr/src/krypton
# Install app dependencies
RUN npm install --unsafe-perm

# Bundle app source


EXPOSE 8080

