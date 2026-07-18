# BizOS Deployment Guide

## Prerequisites
- Docker & Docker Compose
- Kubernetes 1.25+
- Helm (optional)

## Docker Compose
For local production testing:
```bash
docker-compose up -d --build
```

## Kubernetes Deployment
To deploy into a production cluster:
1. Setup namespaces: `kubectl create namespace bizos-prod`
2. Apply secrets: `kubectl apply -f k8s/config.yaml`
3. Apply PVCs: `kubectl apply -f k8s/pvc.yaml`
4. Apply API & Worker deployments: `kubectl apply -f k8s/deployment.yaml`
5. Expose Services: `kubectl apply -f k8s/service.yaml -f k8s/ingress.yaml`
6. Apply Autoscaling: `kubectl apply -f k8s/hpa.yaml`

## Verification
- Check pods: `kubectl get pods -n bizos-prod`
- View logs: `kubectl logs -l app=bizos -n bizos-prod`
