# ML k8s (gke) stack

## Setup

<details><summary> Show </summary>

### Service account
TODO: Set roles also.
```bash
gcloud iam service-accounts create ml-api
```

### Secrets
TODO: Set apikeys here.

```bash
echo -n "$SECRETS" | gcloud secrets create ml-api-secret --data-file=-
```

</details>

## Deploying
```
./scripts/deploy.sh <local|dev|pro>
```
