# Data Model: Local Kubernetes Deployment of AI Todo Chatbot

## Kubernetes Resources

### Deployment
- **apiVersion**: apps/v1
- **kind**: Deployment
- **metadata**: name, namespace, labels
- **spec**:
  - replicas: number of pod replicas
  - selector: label selector for pods
  - template: pod template
    - containers: list of containers
      - name: container name
      - image: Docker image reference
      - ports: container ports
      - env: environment variables
      - resources: CPU/memory limits and requests

### Service
- **apiVersion**: v1
- **kind**: Service
- **metadata**: name, namespace, labels
- **spec**:
  - selector: label selector for pods
  - ports: service ports
  - type: Service type (ClusterIP, NodePort, LoadBalancer)
  - clusterIP: internal IP address (optional)

### Ingress
- **apiVersion**: networking.k8s.io/v1
- **kind**: Ingress
- **metadata**: name, namespace, annotations
- **spec**:
  - rules: routing rules
    - host: hostname
    - http: HTTP routing
      - paths: path-based routing
  - tls: TLS configuration (optional)

### ConfigMap
- **apiVersion**: v1
- **kind**: ConfigMap
- **metadata**: name, namespace, labels
- **data**: key-value pairs of configuration data

### Secret
- **apiVersion**: v1
- **kind**: Secret
- **metadata**: name, namespace, labels
- **data**: base64-encoded sensitive data
- **stringData**: plain text sensitive data (encoded automatically)

## Helm Chart Structure

### Chart.yaml
- **apiVersion**: Helm chart API version
- **name**: Chart name
- **version**: Chart version
- **appVersion**: Application version
- **description**: Chart description

### values.yaml
- **replicaCount**: Number of pod replicas
- **image**: Container image configuration
  - repository: Image repository
  - pullPolicy: Image pull policy
  - tag: Image tag
- **service**: Service configuration
  - type: Service type
  - port: Service port
- **ingress**: Ingress configuration
  - enabled: Whether to enable ingress
  - hosts: List of hostnames
  - tls: TLS configuration
- **resources**: Resource limits and requests
- **nodeSelector**: Node selection constraints
- **tolerations**: Taint tolerations
- **affinity**: Pod affinity/anti-affinity rules

## Application Configuration

### Environment Variables
- **APP_ENV**: Application environment (development, staging, production)
- **PORT**: Application port number
- **DATABASE_URL**: Database connection string (if applicable)
- **OPENAI_API_KEY**: OpenAI API key for AI features (stored in Secret)
- **LOG_LEVEL**: Logging level (debug, info, warn, error)

### Resource Requirements
- **CPU**: Minimum and maximum CPU allocation
- **Memory**: Minimum and maximum memory allocation
- **Storage**: Persistent storage requirements (if applicable)