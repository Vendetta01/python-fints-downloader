
#PYTHON:=python
REGISTRY:=npodewitz
IMAGE_NAME:=fints-downloader
CONTAINER_NAME:=${IMAGE_NAME}
DOCKER_RUN_ARGS:=-p 8080:8080

.PHONY: run migrate clean build build-nc clean-run tag png


run: migrate
	@echo "Running webserver..."
	./src/manage.py runserver 8080

migrate:
	@echo "Make migrations..."
	./src/manage.py makemigrations
	@echo "Migrating..."
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

diagram:
	@echo "Creating PNG of plantuml diagram..."
	java -jar bin/plantuml.jar -o out/model/ -tpng model.plantuml
	java -jar bin/plantuml.jar -o out/model/ -tsvg model.plantuml
#	java -jar bin/plantuml.jar -o out/model/ -tpdf model.plantuml
