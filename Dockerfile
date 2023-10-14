FROM python:3.9-alpine

# Source repository ENV variables
ENV REPO_URL=https://github.com/netbox-community/devicetype-library.git
ENV REPO_BRANCH=master

# Netbox ENV variables
ENV NETBOX_URL=''
ENV NETBOX_TOKEN=''
ENV REPO_BRANCH=master
ENV IGNORE_SSL_ERRORS=False

WORKDIR /app
COPY requirements.txt .

# Install dependencies
RUN apk add --no-cache git ca-certificates && \
    python3 -m pip install --upgrade pip && \
    pip3 install -r requirements.txt

# Copy over src code
COPY *.py ./

# -u to avoid stdout buffering
ENTRYPOINT ["python3","-u","nb-dt-import.py"]
