
#PYTHON:=python
REGISTRY:=npodewitz
IMAGE_NAME:=fints-downloader
CONTAINER_NAME:=${IMAGE_NAME}
DOCKER_RUN_ARGS:=-p 8080:8080

.PHONY: run migrate clean build build-nc clean-run tag model run_backend


run: migrate
	@echo "Running webserver..."
	source ./env/bin/activate; \
	./src/manage.py runserver 8080

run_backend:
	@echo "Running backend..."
	source ./env/bin/activate; \
	./src/backend/start.sh

migrate:
	@echo "Make migrations..."
	source ./env/bin/activate; \
	./src/manage.py makemigrations
	@echo "Migrating..."
	source ./env/bin/activate; \
	./src/manage.py migrate

clean:
	@echo "Cleaning up..."

clean-run: clean run

build: migrate
	@echo "Building docker image..."
	docker build -t ${IMAGE_NAME} .

build-nc: migrate
	@echo "Building docker image without cache..."
	docker build --no-cache -t ${IMAGE_NAME} .

docker-run: build
	@echo "Running docker container..."
	docker run -it --rm -p 8080:80 -p 8443:443 --name fints-downloader fints-downloader:latest

model:
	@echo "Generating model..."
	source ./env/bin/activate; \
	./src/manage.py graph_models -t django2018 -o out/model/fints_downloader_generated.png fints_downloader; \
	java -jar bin/plantuml.jar -o out/model/ -tpng model.plantuml; \
	java -jar bin/plantuml.jar -o out/model/ -tsvg model.plantuml
#	java -jar bin/plantuml.jar -o out/model/ -tpdf model.plantuml
