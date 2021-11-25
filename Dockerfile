FROM python:3.9-alpine

ENV REPO_URL=https://github.com/netbox-community/devicetype-library.git
WORKDIR /app
COPY requirements.txt .

# Install dependencies
RUN apk add --no-cache git ca-certificates && \
    python3 -m pip install --upgrade pip && \
    pip3 install -r requirements.txt

# Copy over src code
COPY *.py ./

# -u to avoid stdout buffering
CMD ["python3","-u","nb-dt-import.py"]
