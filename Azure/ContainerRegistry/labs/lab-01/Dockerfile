FROM alpine:3.22

LABEL maintainer="Adrian"
LABEL description="Dummy image for Azure Container Registry practice"

WORKDIR /app

COPY hello.txt .

CMD ["sh", "-c", "echo 'Container iniciado'; cat hello.txt; tail -f /dev/null"]