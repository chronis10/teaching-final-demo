# Teaching Platform Final Demo


### Example
To test the custom module:

```bash
# Only if you're using the arm64 architecture 
export ARCH=arm64  

# Extend the Dockerfile with custom dependencies
cd custom_containers
docker build --build-arg ARCH=${ARCH:-amd64} -f Dockerfile_ai_toolkit -t chronis10/teaching-ai-toolkit:${ARCH:-amd64} .
cd ..

docker-compose up
```

### Develop
1. Use the custom_modules/rl_graz_module.py file as a template to create your custom script AI-toolkit module. Save it, for instance, in the custom_modules/ directory.

2. Create your custom Dockerfile. If you have additional dependencies like numpy, use custom_containers/Dockerfile_ai_toolkit as a template.

3. Modify or create a new docker-compose file.

```bash
  your_module_name:
    image: "chronis10/teaching-ai-toolkit:${ARCH:-amd64}"
    container_name: your_container_name
    depends_on: 
      - rabbitmq
    restart: on-failure
    environment:
      - SERVICE_TYPE=modules.your_module_filename.your_module_class_name
      - SERVICE_NAME=your_module_filename
      - TOPICS=sensor.your_module_topic.value
      - MODEL_PATH=/app/storage/s4181_model.h5
      - PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
    env_file:
      - env/rabbitmq_client.env
    volumes:
      - $PWD/model/s4181_model.h5:/app/storage/s4181_model.h5
      - $PWD/custom_modules/your_module_filename:/app/modules/your_module_filename
```

Docker Compose will automatically attach your module to the modules directory of the AI-toolkit and start your custom service.

```bash
 volumes:
      - .........
      - $PWD/custom_modules/your_module_filename:/app/modules/your_module_filename
```
This method is also suitable for development. In the same manner, you can modify and hot-plug any service or module of the Teaching Platform.   

### Distribute
After testing and making modifications, you can use docker push to release the updated image to Docker Hub.


