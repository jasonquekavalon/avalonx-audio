SERVICE_DEPLOYMENT_VERSION="latest"
DEPLOYMENT_VERSION="latest"
IMAGE_VERSION="$SHORT_SHA"
PROJECT_ID="avalonx-dev"

# Always update the image version label
sed -i s/"<IMAGE_VERSION>"/"$IMAGE_VERSION"/g deployment.yaml
