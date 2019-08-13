FROM nvcr.io/nvidia/digits:19.06-tensorflow
LABEL maintainer="National Institute of Standards and Technology"

ENV WIPP_API_URL localhost:8080/api

# Update pip
RUN pip install --upgrade pip

COPY wipp /opt/digits/plugins/data/wipp

# Change working directory to WIPP data ingestion plugin source path
WORKDIR /opt/digits/plugins/data/wipp

# Install WIPP data plugin
RUN pip install .

# Reset default working directory
WORKDIR /workspace
