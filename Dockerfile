FROM alpine:3.3

MAINTAINER NYU-Products

# Install just the Python runtime (no dev)

RUN apk add --update \
python \
py-pip \
&& rm -rf /var/cache/apk/*

ENV PORT 5000
EXPOSE $PORT

# Set up a working folder and install the pre-reqs
WORKDIR /app
ADD requirements.txt /app
RUN pip install -r requirements.txt

# Add the code as the last Docker layer because it changes the most
ADD static /app/static
ADD server.py /app
ADD models.py /app

# Run the service
CMD [ "python", "server.py" ]
