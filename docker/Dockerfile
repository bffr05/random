
# Start from python:3.8-alpine base image
FROM python:3.10

# The latest alpine images don't have some tools like (`git` and `bash`).
# Adding git, bash and openssh to the image

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt



