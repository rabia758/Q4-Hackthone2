# Quickstart: Local Kubernetes Deployment of AI Todo Chatbot

## Prerequisites

1. **Docker Desktop** with Kubernetes enabled OR **Minikube** installed
2. **kubectl** command-line tool
3. **Helm** package manager
4. **kubectl-ai** plugin (optional, for AI-assisted operations)
5. **kagent** (optional, for AI-assisted operations)

## Setup Instructions

### 1. Start Minikube (if using Minikube instead of Docker Desktop Kubernetes)

```bash
minikube start
```

### 2. Build the Docker image for the AI Todo Chatbot

```bash
# Navigate to the Phase III chatbot directory
cd phase-3-chatbot

# Build the Docker image
docker build -t ai-todo-chatbot:latest .

# If using Minikube, load the image into the cluster
minikube image load ai-todo-chatbot:latest
```

### 3. Deploy using Helm

```bash
# Navigate to the Helm chart directory
cd phase-4-local-k8s/helm

# Install the Helm chart
helm install ai-todo-chatbot .
```

### 4. Access the Application

```bash
# Get the service URL
kubectl get svc ai-todo-chatbot-service

# If using Minikube, get the service URL
minikube service ai-todo-chatbot-service --url

# Or create an ingress and access via browser
kubectl get ingress ai-todo-chatbot-ingress
```

## AI-Assisted Operations

### Deploy with AI assistance
```bash
kubectl ai create deployment ai-todo-chatbot --image=ai-todo-chatbot:latest
```

### Scale with AI assistance
```bash
kubectl ai scale deployment ai-todo-chatbot --replicas=3
```

### Debug with AI assistance
```bash
kubectl ai debug pod -l app=ai-todo-chatbot
```

## Verification

1. Check that all pods are running:
   ```bash
   kubectl get pods
   ```

2. Check that the service is accessible:
   ```bash
   kubectl get svc
   ```

3. Verify the application is responding:
   ```bash
   curl [SERVICE_URL]
   ```

## Troubleshooting

- If pods are not starting, check logs: `kubectl logs -l app=ai-todo-chatbot`
- If service is not accessible, verify ingress: `kubectl get ingress`
- If Docker build fails, ensure all dependencies from Phase III are properly included