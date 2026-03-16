# This is a sample Dockerfile for a minimal image with Python, Lua, and the Lua
# dependencies to run CtGen

FROM python:3.9-alpine

RUN apk add --no-cache lua5.4 lua5.4-dev luarocks5.4

# Unfortunately I cannot just say 'lua' and 'lua-dev' to pick the latests,
# because apk installs lua5.4 and lua5.1-dev ... sigh

# Create some symlinks for the user's sanity...
RUN ln -s /usr/bin/lua5.4 /usr/bin/lua  &&  ln -s /usr/bin/luarocks-5.4 /usr/bin/luarocks

# Lua dependencies
RUN luarocks install template-text && rm -rf /var/cache/*


### Example commands

## From this folder:
# docker build -t ctgen .

## From the root of the repo:
# docker run -it --mount type=bind,src=$(pwd),dst=/root/ctgen ctgen

## Inside the container:
# cd /root/ctgen/
# pip install --break-system-packages .
# cd sample/basic
# ctgen -c config.yaml --lang cpp_iitrbd -o gen/cpp/       model.motdsl
# ctgen -c config.yaml --lang octave     -o gen/octave/    model.motdsl
# ctgen -c config.yaml --lang plaintext  -o gen/plaintext/ model.motdsl
# ctgen -c config.yaml -s 50             -o gen/octave     model.motdsl
