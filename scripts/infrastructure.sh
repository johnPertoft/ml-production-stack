#!/usr/bin/env bash
set -e

# TODO: Support create, destroy commands?

# TODO: Don't create if exists.
# TODO: Replace this with terraform? Or gcp deployment manager?

# TODO: Handle setup of minikube as well?
# minikube start
# minikube tunnel
# minikube addons enable ingress

# TODO: Create static ip adresses

#gcloud compute addresses create ml-api-ip --region europe-north1


gcloud container clusters create test-cluster-1 \
    --project=kubernetes-test-297213 \
    --zone=europe-north1-a \
    --num-nodes=2 \
    --machine-type=n1-standard-2 \
    --disk-size=32GB
