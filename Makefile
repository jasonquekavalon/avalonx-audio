BUILD_COMMIT=$(shell [[ -z "$(SHA_DOCKERFILE)" ]] && git log --pretty=format:'%h' -n 1 || echo "$(SHA_DOCKERFILE)")
BUILD_DATE=$(shell TZ=Utc date +%Y%m%d)
BUILD_TIME=$(shell TZ=Utc date +%H%M%S)
BUILD_DIR=build
BUILD_RELEASE=$(shell [[ -z "$(TAG_DOCKERFILE)" ]] && git describe --tags || echo "$(TAG_DOCKERFILE)")
SERVICE_NAME=$(shell basename "$(PWD)")
docker-build:
	docker build -t ${SERVICE_NAME} .

dev-release:
	pipenv run pipenv_to_requirements -f
	docker build -t eu.gcr.io/avalonx-dev/${SERVICE_NAME}:${BUILD_DATE}${BUILD_TIME} .
	docker push eu.gcr.io/avalonx-dev/${SERVICE_NAME}:${BUILD_DATE}${BUILD_TIME}
	cat deployment_template.yaml | sed s/"<IMAGE_VERSION>"/"${BUILD_DATE}${BUILD_TIME}"/g > deployment_latest.yaml
	kubectl apply -f deployment_latest.yaml