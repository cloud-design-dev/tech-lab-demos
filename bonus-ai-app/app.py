import os
import json
import logging
from datetime import datetime

import numpy as np
from flask import Flask, request, jsonify, render_template
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import ARRAY

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("ChromaDB not available, using fallback storage")

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logging.warning("SentenceTransformers not available, using random embeddings")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///ai_demo.db')
VECTOR_DB_PATH = os.environ.get('VECTOR_DB_PATH', '/data/vectordb')
MODEL_NAME = os.environ.get('MODEL_NAME', 'all-MiniLM-L6-v2')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(ARRAY(Float), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(Text, nullable=True)

Base.metadata.create_all(bind=engine)

class VectorStore:
    def __init__(self):
        self.model = None
        self.chroma_client = None
        self.collection = None
        self.fallback_docs = []
        
        if EMBEDDINGS_AVAILABLE:
            try:
                self.model = SentenceTransformer(MODEL_NAME)
                logging.info(f"Loaded embedding model: {MODEL_NAME}")
            except Exception as e:
                logging.error(f"Failed to load embedding model: {e}")
        
        if CHROMADB_AVAILABLE:
            try:
                os.makedirs(VECTOR_DB_PATH, exist_ok=True)
                self.chroma_client = chromadb.PersistentClient(
                    path=VECTOR_DB_PATH,
                    settings=Settings(anonymized_telemetry=False)
                )
                self.collection = self.chroma_client.get_or_create_collection(
                    name="documents",
                    metadata={"hnsw:space": "cosine"}
                )
                logging.info(f"Connected to ChromaDB at {VECTOR_DB_PATH}")
            except Exception as e:
                logging.error(f"Failed to initialize ChromaDB: {e}")
    
    def embed_text(self, text):
        if self.model:
            return self.model.encode(text).tolist()
        else:
            return np.random.rand(384).tolist()
    
    def add_document(self, doc_id, title, content, metadata=None):
        embedding = self.embed_text(content)
        
        if self.collection:
            try:
                self.collection.add(
                    documents=[content],
                    metadatas=[{"title": title, "metadata": metadata or ""}],
                    ids=[str(doc_id)],
                    embeddings=[embedding]
                )
            except Exception as e:
                logging.error(f"Failed to add to ChromaDB: {e}")
        
        self.fallback_docs.append({
            "id": doc_id,
            "title": title,
            "content": content,
            "embedding": embedding,
            "metadata": metadata
        })
        
        db = SessionLocal()
        try:
            doc = Document(
                id=doc_id,
                title=title,
                content=content,
                embedding=embedding,
                metadata=json.dumps(metadata) if metadata else None
            )
            db.merge(doc)
            db.commit()
        except Exception as e:
            logging.error(f"Failed to save to database: {e}")
            db.rollback()
        finally:
            db.close()
    
    def search(self, query, n_results=5):
        query_embedding = self.embed_text(query)
        
        if self.collection:
            try:
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results
                )
                return [
                    {
                        "id": results["ids"][0][i],
                        "title": results["metadatas"][0][i]["title"],
                        "content": results["documents"][0][i],
                        "distance": results["distances"][0][i] if "distances" in results else 0
                    }
                    for i in range(len(results["ids"][0]))
                ]
            except Exception as e:
                logging.error(f"ChromaDB search failed: {e}")
        
        similarities = []
        for doc in self.fallback_docs:
            similarity = np.dot(query_embedding, doc["embedding"])
            similarities.append((similarity, doc))
        
        similarities.sort(key=lambda x: x[0], reverse=True)
        return [
            {
                "id": doc["id"],
                "title": doc["title"],
                "content": doc["content"],
                "distance": 1 - sim
            }
            for sim, doc in similarities[:n_results]
        ]

vector_store = VectorStore()

request_stats = {
    "total_requests": 0,
    "search_requests": 0,
    "add_requests": 0,
    "errors": 0
}

@app.route('/')
def index():
    return render_template('index.html', stats=request_stats)

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "vector_db_available": CHROMADB_AVAILABLE,
        "embeddings_available": EMBEDDINGS_AVAILABLE,
        "stats": request_stats
    })

@app.route('/api/documents', methods=['POST'])
def add_document():
    try:
        request_stats["total_requests"] += 1
        request_stats["add_requests"] += 1
        
        data = request.get_json()
        if not data or 'title' not in data or 'content' not in data:
            return jsonify({"error": "Missing title or content"}), 400
        
        doc_id = data.get('id', len(vector_store.fallback_docs) + 1)
        title = data['title']
        content = data['content']
        metadata = data.get('metadata', {})
        
        vector_store.add_document(doc_id, title, content, metadata)
        
        return jsonify({
            "message": "Document added successfully",
            "id": doc_id
        })
    
    except Exception as e:
        request_stats["errors"] += 1
        logging.error(f"Error adding document: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/search', methods=['POST'])
def search_documents():
    try:
        request_stats["total_requests"] += 1
        request_stats["search_requests"] += 1
        
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"error": "Missing query"}), 400
        
        query = data['query']
        n_results = data.get('n_results', 5)
        
        results = vector_store.search(query, n_results)
        
        return jsonify({
            "query": query,
            "results": results,
            "count": len(results)
        })
    
    except Exception as e:
        request_stats["errors"] += 1
        logging.error(f"Error searching documents: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def list_documents():
    try:
        request_stats["total_requests"] += 1
        
        db = SessionLocal()
        try:
            docs = db.query(Document).all()
            return jsonify({
                "documents": [
                    {
                        "id": doc.id,
                        "title": doc.title,
                        "content": doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                        "created_at": doc.created_at.isoformat() if doc.created_at else None
                    }
                    for doc in docs
                ],
                "count": len(docs)
            })
        finally:
            db.close()
    
    except Exception as e:
        request_stats["errors"] += 1
        logging.error(f"Error listing documents: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    sample_docs = [
        {
            "title": "OpenShift Container Platform",
            "content": "OpenShift is a family of containerization software products developed by Red Hat. It provides a cloud computing platform as a service (PaaS) for developing and deploying applications."
        },
        {
            "title": "Kubernetes Fundamentals",
            "content": "Kubernetes is an open-source container orchestration platform that automates the deployment, scaling, and management of containerized applications."
        },
        {
            "title": "Vector Databases",
            "content": "Vector databases are specialized databases designed to store and query high-dimensional vectors, commonly used in machine learning and AI applications for similarity search."
        }
    ]
    
    for i, doc in enumerate(sample_docs, 1):
        vector_store.add_document(i, doc["title"], doc["content"])
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('DEBUG', 'False').lower() == 'true')