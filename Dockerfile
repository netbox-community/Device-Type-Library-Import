FROM python:3.9-alpine
COPY requirements.txt .
RUN apk add --no-cache git
RUN pip3 install -r requirements.txt

# default
ENV REPO_URL=https://github.com/netbox-community/devicetype-library.git
WORKDIR /app
COPY *.py ./

# -u to avoid stdout buffering
CMD ["python","-u","nb-dt-import.py"]
