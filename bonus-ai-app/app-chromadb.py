#!/usr/bin/env python3

import os
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional

import numpy as np
from flask import Flask, request, jsonify, render_template
from anthropic import Anthropic
import chromadb
from chromadb.config import Settings
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class CatFactsAI:
    def __init__(self):
        # Initialize Anthropic client
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.anthropic_api_key:
            logger.error("ANTHROPIC_API_KEY environment variable not set")
            raise ValueError("Anthropic API key is required")
        
        self.anthropic = Anthropic(api_key=self.anthropic_api_key)
        
        # Initialize ChromaDB (vector database)
        try:
            # Try newer API first
            self.chroma_client = chromadb.PersistentClient(path="/data/chroma")
        except Exception as e:
            logger.warning(f"Failed to create PersistentClient, trying legacy API: {e}")
            # Fallback to older API
            self.chroma_client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory="/data/chroma"
            ))
        
        # Create or get collection for cat facts
        try:
            self.collection = self.chroma_client.get_or_create_collection(
                name="cat_facts",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            logger.warning(f"Failed to create collection with metadata, trying without: {e}")
            self.collection = self.chroma_client.get_or_create_collection(
                name="cat_facts"
            )
        
        logger.info("CatFactsAI initialized successfully")
    
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
        # Create a unique ID for the fact
        fact_id = hashlib.md5(f"{fact}_{datetime.utcnow().isoformat()}".encode()).hexdigest()
        
        # Add to ChromaDB
        self.collection.add(
            documents=[fact],
            metadatas=[{
                "query": query or "general",
                "timestamp": datetime.utcnow().isoformat(),
                "model": "claude-3-haiku-20240307"
            }],
            ids=[fact_id]
        )
        
        return fact_id
    
    def search_similar_facts(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for similar cat facts in the vector database"""
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
    
    def get_all_facts(self, limit: int = 20) -> List[Dict]:
        """Get all stored cat facts"""
        try:
            # Get all facts from the collection
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
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            count = self.collection.count()
            return {
                "total_facts": count,
                "database_type": "ChromaDB (Vector Database)",
                "model": "claude-3-haiku-20240307",
                "collection_name": "cat_facts"
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
    return jsonify({
        "status": "healthy",
        "anthropic_configured": cat_ai is not None,
        "vector_db": "ChromaDB" if cat_ai else "Not initialized",
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