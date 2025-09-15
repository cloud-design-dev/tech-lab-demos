# AI Vector Search Demo App

A Flask-based AI application demonstrating vector search capabilities using ChromaDB, designed for deployment on OpenShift with persistent vector database storage.

## Features

- **Vector Search**: Semantic search using sentence transformers and ChromaDB
- **Document Management**: Add and search documents with AI-powered embeddings
- **Persistent Storage**: Vector database backed by OpenShift PVC
- **Fallback Support**: Graceful degradation when dependencies are unavailable
- **Health Monitoring**: Built-in health checks and request statistics
- **OpenShift Ready**: Complete deployment manifests included

## Architecture

- **Frontend**: HTML/CSS/JavaScript with real-time search interface
- **Backend**: Flask application with SQLAlchemy ORM
- **Vector DB**: ChromaDB for similarity search with cosine distance
- **Embeddings**: SentenceTransformers (all-MiniLM-L6-v2 model)
- **Storage**: PostgreSQL/SQLite for metadata, PVC for vector data

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py

# Test the application
python -c "from app import app; print('✓ App imports successfully')"
```

## OpenShift Deployment

### 1. Build and Deploy

```bash
# Create the project
oc new-project ai-demo

# Apply the build configuration
oc apply -f openshift/buildconfig.yaml

# Start the build
oc start-build ai-demo-build

# Deploy the application
oc apply -f openshift/deployment.yaml
```

### 2. Verify Deployment

```bash
# Check pod status
oc get pods -l app=ai-demo

# Check PVC
oc get pvc vectordb-pvc

# Check route
oc get route ai-demo-route

# View logs
oc logs -f deployment/ai-demo-app
```

### 3. Access the Application

```bash
# Get the route URL
oc get route ai-demo-route -o jsonpath='{.spec.host}'
```

## API Endpoints

- `GET /` - Web interface
- `GET /health` - Health check and statistics
- `POST /api/documents` - Add new document
- `POST /api/search` - Search documents
- `GET /api/documents` - List all documents

## Environment Variables

- `VECTOR_DB_PATH` - Path to ChromaDB storage (default: `/data/vectordb`)
- `DATABASE_URL` - SQLAlchemy database URL
- `MODEL_NAME` - SentenceTransformer model name
- `PORT` - Application port (default: 5000)
- `DEBUG` - Enable debug mode

## Storage Requirements

- **PVC Size**: 5Gi (configurable in deployment.yaml)
- **Access Mode**: ReadWriteOnce
- **Storage Class**: Uses cluster default

## Resource Limits

- **Memory**: 512Mi request, 1Gi limit
- **CPU**: 250m request, 500m limit
- **Replicas**: 1 (single instance due to PVC constraints)

## Sample Data

The application includes sample documents about:
- OpenShift Container Platform
- Kubernetes Fundamentals  
- Vector Databases

## Monitoring

- Health endpoint at `/health`
- Request statistics tracking
- Liveness and readiness probes configured
- Auto-refresh dashboard every 30 seconds