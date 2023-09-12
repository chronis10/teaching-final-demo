# Modify Containers

Edit the Dockerfile and overwrite or give a new image name.

```bash
docker build --build-arg ARCH=${ARCH:-amd64} -f Dockerfile_ai_toolkit -t chronis10/teaching-ai-toolkit:${ARCH:-amd64} .
```