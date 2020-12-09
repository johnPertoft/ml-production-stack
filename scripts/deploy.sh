#!/usr/bin/env bash
set -e

# TODO: Add --prune to kubectl apply to delete things also?

GCP_PROJECT_ID="kubernetes-test-297213"
CONTAINER_REGISTRY="eu.gcr.io/${GCP_PROJECT_ID}"
K8S_CLUSTER="test-cluster-1"

function print_help {
    echo "Usage: $0 env"
    echo "  env: {dev, pro, local}"
}

if [[ $# -lt 1 ]]; then
    print_help
    exit 1
fi

ENV="${1}"
shift

case ${ENV} in
    local)
        echo "TODO: Fix things to make it work with minikube."
        exit

        if [[ "$(kubectl config current-context)" != "minikube" ]]; then
            minikube start
            minikube addons enable ingress
            echo ""
            echo "Remember to run `minikube tunnel`"
        fi

        API_IMAGE="ml-api-api"
        SERVING_IMAGE="ml-api-serving"

        eval $(minikube -p minikube docker-env)
        docker build -t ${API_IMAGE} -f docker/Dockerfile.api .
        docker build -t ${SERVING_IMAGE} -f docker/Dockerfile.serving .

        export API_IMAGE=${API_IMAGE}
        export API_IMAGE_PULL_POLICY="Never"
        export SERVING_IMAGE=${SERVING_IMAGE}
        export SERVING_IMAGE_PULL_POLICY="Never"
        envsubst < deployment-template.yaml > /tmp/deployment.yaml
        kubectl apply -f /tmp/deployment.yaml
        ;;
    dev|pro)
        API_IMAGE="${CONTAINER_REGISTRY}/ml-api-api"
        SERVING_IMAGE="${CONTAINER_REGISTRY}/ml-api-serving"

        docker build -t ${API_IMAGE} -f docker/Dockerfile.api .
        docker build -t ${SERVING_IMAGE} -f docker/Dockerfile.serving .
        docker push ${API_IMAGE}
        docker push ${SERVING_IMAGE}

        gcloud container clusters get-credentials ${K8S_CLUSTER}

        export API_IMAGE=${API_IMAGE}
        export API_IMAGE_PULL_POLICY="Always"
        export SERVING_IMAGE=${SERVING_IMAGE}
        export SERVING_IMAGE_PULL_POLICY="Always"
        envsubst < deployment-template.yaml > /tmp/deployment.yaml
        kubectl apply -f /tmp/deployment.yaml
        ;;
    *)
        echo "Invalid environment."
        print_help
        exit 1
        ;;
esac

if [[ "$1" == "--restart" ]]; then
    kubectl rollout restart deployment/serving -n ml-api
    kubectl rollout restart deployment/api -n ml-api
fi
