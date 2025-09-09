#!/usr/bin/env python3

import os
import json
import time
import logging
import pickle
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

import numpy as np
from flask import Flask, request, jsonify, render_template
from anthropic import Anthropic
import hashlib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class SimpleVectorDB:
    """Simple vector database implementation using TF-IDF and cosine similarity"""
    
    def __init__(self, data_dir="/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.facts_file = self.data_dir / "cat_facts.json"
        self.vectors_file = self.data_dir / "vectors.pkl"
        
        # Storage for facts and their metadata
        self.facts = []
        self.metadata = []
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        self.vectors = None
        
        # Load existing data
        self._load_data()
        
    def _load_data(self):
        """Load existing facts and vectors from disk"""
        try:
            if self.facts_file.exists():
                with open(self.facts_file, 'r') as f:
                    data = json.load(f)
                    self.facts = data.get('facts', [])
                    self.metadata = data.get('metadata', [])
                
                if self.vectors_file.exists() and self.facts:
                    with open(self.vectors_file, 'rb') as f:
                        vector_data = pickle.load(f)
                        self.vectorizer = vector_data['vectorizer']
                        self.vectors = vector_data['vectors']
                        
            logger.info(f"Loaded {len(self.facts)} facts from storage")
                        
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self.facts = []
            self.metadata = []
    
    def _save_data(self):
        """Save facts and vectors to disk"""
        try:
            # Save facts and metadata
            with open(self.facts_file, 'w') as f:
                json.dump({
                    'facts': self.facts,
                    'metadata': self.metadata
                }, f, indent=2)
            
            # Save vectors
            if self.vectors is not None:
                with open(self.vectors_file, 'wb') as f:
                    pickle.dump({
                        'vectorizer': self.vectorizer,
                        'vectors': self.vectors
                    }, f)
                    
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def add_fact(self, fact: str, metadata: Dict) -> str:
        """Add a new fact to the database"""
        fact_id = hashlib.md5(f"{fact}_{datetime.utcnow().isoformat()}".encode()).hexdigest()
        
        self.facts.append(fact)
        metadata['id'] = fact_id
        self.metadata.append(metadata)
        
        # Rebuild vectors
        self._rebuild_vectors()
        self._save_data()
        
        return fact_id
    
    def _rebuild_vectors(self):
        """Rebuild TF-IDF vectors for all facts"""
        if self.facts:
            try:
                self.vectors = self.vectorizer.fit_transform(self.facts)
            except Exception as e:
                logger.error(f"Error building vectors: {e}")
                self.vectors = None
    
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for similar facts"""
        if not self.facts or self.vectors is None:
            return []
        
        try:
            # Vectorize the query
            query_vector = self.vectorizer.transform([query])
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, self.vectors).flatten()
            
            # Get top results
            top_indices = np.argsort(similarities)[::-1][:limit]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Minimum similarity threshold
                    results.append({
                        "fact": self.facts[idx],
                        "metadata": self.metadata[idx],
                        "similarity": float(similarities[idx])
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
    
    def get_all_facts(self, limit: int = 20) -> List[Dict]:
        """Get all facts"""
        end_idx = min(limit, len(self.facts))
        results = []
        
        for i in range(end_idx):
            results.append({
                "id": self.metadata[i].get('id', f'fact_{i}'),
                "fact": self.facts[i],
                "metadata": self.metadata[i]
            })
        
        return results
    
    def count(self) -> int:
        """Get total number of facts"""
        return len(self.facts)


class CatFactsAI:
    def __init__(self):
        # Initialize Anthropic client
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.anthropic_api_key:
            logger.error("ANTHROPIC_API_KEY environment variable not set")
            raise ValueError("Anthropic API key is required")
        
        self.anthropic = Anthropic(api_key=self.anthropic_api_key)
        
        # Try to initialize ChromaDB first (if available), otherwise use Simple Vector DB
        self.vector_db = self._initialize_vector_db()
        
        logger.info(f"CatFactsAI initialized successfully with {type(self.vector_db).__name__}")
    
    def _initialize_vector_db(self):
        """Try to initialize ChromaDB first, fall back to Simple Vector DB"""
        try:
            # Try ChromaDB first (newer SQLite should work with UBI9 Python 3.12)
            import chromadb
            import sqlite3
            
            # Check SQLite version
            sqlite_version = sqlite3.sqlite_version
            logger.info(f"SQLite version: {sqlite_version}")
            
            # ChromaDB needs SQLite >= 3.35.0
            sqlite_version_parts = [int(x) for x in sqlite_version.split('.')]
            if sqlite_version_parts[0] > 3 or (sqlite_version_parts[0] == 3 and sqlite_version_parts[1] >= 35):
                logger.info("SQLite version is compatible with ChromaDB, attempting to use it...")
                
                chroma_client = chromadb.PersistentClient(path="/data/chroma")
                collection = chroma_client.get_or_create_collection(
                    name="cat_facts",
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info("Successfully initialized ChromaDB!")
                return ChromaDBWrapper(chroma_client, collection)
            else:
                logger.warning(f"SQLite version {sqlite_version} is too old for ChromaDB (needs >= 3.35.0)")
                
        except Exception as e:
            logger.warning(f"ChromaDB initialization failed: {e}")
        
        # Fall back to Simple Vector DB
        logger.info("Using Simple Vector DB as fallback")
        return SimpleVectorDB()


class ChromaDBWrapper:
    """Wrapper to make ChromaDB compatible with SimpleVectorDB interface"""
    
    def __init__(self, client, collection):
        self.client = client
        self.collection = collection
        
    def add_fact(self, fact: str, metadata: dict) -> str:
        fact_id = hashlib.md5(f"{fact}_{datetime.utcnow().isoformat()}".encode()).hexdigest()
        
        self.collection.add(
            documents=[fact],
            metadatas=[metadata],
            ids=[fact_id]
        )
        
        return fact_id
    
    def search(self, query: str, limit: int = 5) -> list[dict]:
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            facts = []
            if results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    facts.append({
                        "fact": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "similarity": 1 - results['distances'][0][i] if results['distances'] else 0
                    })
            
            return facts
            
        except Exception as e:
            logger.error(f"Error searching facts: {str(e)}")
            return []
    
    def get_all_facts(self, limit: int = 20) -> list[dict]:
        try:
            results = self.collection.get(
                limit=limit,
                include=["documents", "metadatas"]
            )
            
            facts = []
            if results['documents']:
                for i, doc in enumerate(results['documents']):
                    facts.append({
                        "id": results['ids'][i],
                        "fact": doc,
                        "metadata": results['metadatas'][i] if results['metadatas'] else {}
                    })
            
            return facts
            
        except Exception as e:
            logger.error(f"Error getting facts: {str(e)}")
            return []
    
    def count(self) -> int:
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Error getting count: {str(e)}")
            return 0
    
    def generate_cat_fact(self, user_query: str = None) -> Dict:
        """Generate a cat fact using Anthropic's Claude (cheapest model: claude-3-haiku)"""
        try:
            if user_query:
                prompt = f"Generate an interesting and educational fact about cats related to: {user_query}. Make it engaging and informative."
            else:
                prompt = "Generate a fascinating, educational, and fun fact about cats. Make it interesting and informative."
            
            # Use claude-3-haiku-20240307 (cheapest model)
            message = self.anthropic.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=150,
                temperature=0.7,
                messages=[{
                    "role": "user", 
                    "content": prompt
                }]
            )
            
            cat_fact = message.content[0].text.strip()
            
            # Store in vector database
            fact_id = self._store_cat_fact(cat_fact, user_query)
            
            return {
                "success": True,
                "cat_fact": cat_fact,
                "fact_id": fact_id,
                "model": "claude-3-haiku-20240307",
                "query": user_query,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating cat fact: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _store_cat_fact(self, fact: str, query: str = None) -> str:
        """Store cat fact in vector database"""
        metadata = {
            "query": query or "general",
            "timestamp": datetime.utcnow().isoformat(),
            "model": "claude-3-haiku-20240307"
        }
        
        return self.vector_db.add_fact(fact, metadata)
    
    def search_similar_facts(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for similar cat facts in the vector database"""
        try:
            return self.vector_db.search(query, limit)
        except Exception as e:
            logger.error(f"Error searching facts: {str(e)}")
            return []
    
    def get_all_facts(self, limit: int = 20) -> List[Dict]:
        """Get all stored cat facts"""
        try:
            return self.vector_db.get_all_facts(limit)
        except Exception as e:
            logger.error(f"Error getting facts: {str(e)}")
            return []
    
    def get_stats(self) -> dict:
        """Get database statistics"""
        try:
            count = self.vector_db.count()
            db_type = "ChromaDB (Vector Database)" if isinstance(self.vector_db, ChromaDBWrapper) else "Simple Vector DB (TF-IDF + Cosine Similarity)"
            storage_backend = "SQLite + Vector Index" if isinstance(self.vector_db, ChromaDBWrapper) else "JSON + Pickle"
            
            return {
                "total_facts": count,
                "database_type": db_type,
                "model": "claude-3-haiku-20240307",
                "storage_backend": storage_backend
            }
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {"error": str(e)}

# Initialize the AI service
try:
    cat_ai = CatFactsAI()
except Exception as e:
    logger.error(f"Failed to initialize CatFactsAI: {e}")
    cat_ai = None

@app.route('/')
def home():
    """Home page with UI for the cat facts AI"""
    return render_template('index.html')

@app.route('/api/health')
def health():
    """Health check endpoint"""
    vector_db_type = "Not initialized"
    if cat_ai:
        if isinstance(cat_ai.vector_db, ChromaDBWrapper):
            vector_db_type = "ChromaDB (Vector Database)"
        else:
            vector_db_type = "Simple Vector DB (TF-IDF)"
    
    return jsonify({
        "status": "healthy",
        "anthropic_configured": cat_ai is not None,
        "vector_db": vector_db_type,
        "python_version": f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/api/cat-fact', methods=['GET', 'POST'])
def get_cat_fact():
    """Generate a new cat fact"""
    if not cat_ai:
        return jsonify({"error": "AI service not initialized"}), 500
    
    query = None
    if request.method == 'POST':
        data = request.get_json()
        query = data.get('query') if data else None
    else:
        query = request.args.get('query')
    
    result = cat_ai.generate_cat_fact(query)
    return jsonify(result)

@app.route('/api/search', methods=['POST'])
def search_facts():
    """Search for similar cat facts"""
    if not cat_ai:
        return jsonify({"error": "AI service not initialized"}), 500
    
    data = request.get_json()
    query = data.get('query', '')
    limit = data.get('limit', 5)
    
    if not query:
        return jsonify({"error": "Query is required"}), 400
    
    results = cat_ai.search_similar_facts(query, limit)
    return jsonify({
        "query": query,
        "results": results,
        "count": len(results)
    })

@app.route('/api/facts')
def get_facts():
    """Get all stored cat facts"""
    if not cat_ai:
        return jsonify({"error": "AI service not initialized"}), 500
    
    limit = request.args.get('limit', 20, type=int)
    facts = cat_ai.get_all_facts(limit)
    
    return jsonify({
        "facts": facts,
        "count": len(facts)
    })

@app.route('/api/stats')
def get_stats():
    """Get database statistics"""
    if not cat_ai:
        return jsonify({"error": "AI service not initialized"}), 500
    
    stats = cat_ai.get_stats()
    return jsonify(stats)

@app.route('/api/demo')
def demo():
    """Demo endpoint that generates multiple facts for testing"""
    if not cat_ai:
        return jsonify({"error": "AI service not initialized"}), 500
    
    demo_queries = [
        "behavior",
        "hunting",
        "sleeping",
        "communication",
        "history"
    ]
    
    results = []
    for query in demo_queries:
        result = cat_ai.generate_cat_fact(query)
        if result.get('success'):
            results.append(result)
        time.sleep(1)  # Rate limiting
    
    return jsonify({
        "demo_facts": results,
        "count": len(results)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)