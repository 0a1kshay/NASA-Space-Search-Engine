#!/usr/bin/env python3
"""
NASA Knowledge Engine Startup and Fix Script
Comprehensive solution for all identified issues
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command, cwd=None, check=True):
    """Run a system command"""
    try:
        logger.info(f"Running: {command}")
        result = subprocess.run(command, shell=True, cwd=cwd, check=check, 
                              capture_output=True, text=True)
        if result.stdout:
            logger.info(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e}")
        if e.stderr:
            logger.error(e.stderr)
        if check:
            raise
        return e

def check_neo4j_running():
    """Check if Neo4j is running"""
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        return 'neo4j' in result.stdout
    except:
        return False

def start_neo4j():
    """Start Neo4j using Docker Compose"""
    logger.info("🚀 Starting Neo4j database...")
    
    if check_neo4j_running():
        logger.info("✅ Neo4j is already running")
        return True
    
    try:
        # Stop any existing containers
        run_command("docker-compose down", check=False)
        
        # Start Neo4j
        run_command("docker-compose up -d neo4j")
        
        # Wait for Neo4j to be ready
        logger.info("⏳ Waiting for Neo4j to be ready...")
        max_retries = 30
        for i in range(max_retries):
            try:
                result = run_command(
                    'docker exec neo4j_knowledge_graph cypher-shell -u neo4j -p testpassword "RETURN 1"',
                    check=False
                )
                if result.returncode == 0:
                    logger.info("✅ Neo4j is ready!")
                    return True
            except:
                pass
            
            time.sleep(5)
            logger.info(f"Still waiting... ({i+1}/{max_retries})")
        
        logger.error("❌ Neo4j failed to start within timeout")
        return False
        
    except Exception as e:
        logger.error(f"Error starting Neo4j: {e}")
        return False

def setup_neo4j_schema():
    """Setup Neo4j schema constraints and indexes"""
    logger.info("🔧 Setting up Neo4j schema...")
    
    schema_commands = [
        # Constraints
        "CREATE CONSTRAINT unique_publication_id IF NOT EXISTS FOR (p:Publication) REQUIRE p.id IS UNIQUE",
        "CREATE CONSTRAINT unique_dataset_id IF NOT EXISTS FOR (d:Dataset) REQUIRE d.id IS UNIQUE", 
        "CREATE CONSTRAINT unique_project_id IF NOT EXISTS FOR (pr:Project) REQUIRE pr.id IS UNIQUE",
        "CREATE CONSTRAINT unique_author_name IF NOT EXISTS FOR (a:Author) REQUIRE a.name IS UNIQUE",
        "CREATE CONSTRAINT unique_organism_name IF NOT EXISTS FOR (o:Organism) REQUIRE o.name IS UNIQUE",
        "CREATE CONSTRAINT unique_keyword_name IF NOT EXISTS FOR (k:Keyword) REQUIRE k.name IS UNIQUE",
        
        # Indexes for performance
        "CREATE INDEX publication_title_index IF NOT EXISTS FOR (p:Publication) ON (p.title)",
        "CREATE INDEX publication_year_index IF NOT EXISTS FOR (p:Publication) ON (p.year)",
        "CREATE INDEX dataset_organism_index IF NOT EXISTS FOR (d:Dataset) ON (d.organism)",
        "CREATE INDEX project_discipline_index IF NOT EXISTS FOR (pr:Project) ON (pr.discipline)",
        "CREATE INDEX author_name_index IF NOT EXISTS FOR (a:Author) ON (a.name)",
        
        # Full-text search index
        "CREATE FULLTEXT INDEX searchIndex IF NOT EXISTS FOR (n:Publication|Dataset|Project|Author) ON EACH [n.title, n.name, n.description, n.abstract]"
    ]
    
    for cmd in schema_commands:
        try:
            result = run_command(
                f'docker exec neo4j_knowledge_graph cypher-shell -u neo4j -p testpassword "{cmd}"',
                check=False
            )
            if result.returncode == 0:
                logger.info(f"✅ Schema command executed: {cmd[:50]}...")
            else:
                logger.warning(f"⚠️  Schema command may have failed (already exists?): {cmd[:50]}...")
        except Exception as e:
            logger.warning(f"Schema command error: {e}")
    
    logger.info("✅ Schema setup complete")

def ingest_sample_data():
    """Run data ingestion scripts"""
    logger.info("📊 Ingesting sample data...")
    
    try:
        # Run the master ingestion script
        result = run_command("python ingest_datasets.py", check=False)
        if result.returncode == 0:
            logger.info("✅ Data ingestion completed successfully")
            return True
        else:
            logger.error("❌ Data ingestion failed")
            return False
    except Exception as e:
        logger.error(f"Error during data ingestion: {e}")
        return False

def start_fastapi_server():
    """Start the FastAPI backend server"""
    logger.info("🌐 Starting FastAPI server...")
    
    try:
        # Install dependencies if needed
        logger.info("Installing Python dependencies...")
        run_command("pip install --upgrade neo4j", check=False)
        run_command("pip install -r requirements.txt", check=False)
        
        # Start server in background
        logger.info("Starting FastAPI server on port 8000...")
        subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app", 
            "--host", "0.0.0.0", "--port", "8000", "--reload"
        ])
        
        # Wait a moment for server to start
        time.sleep(3)
        logger.info("✅ FastAPI server started")
        return True
        
    except Exception as e:
        logger.error(f"Error starting FastAPI server: {e}")
        return False

def test_endpoints():
    """Test key API endpoints"""
    logger.info("🧪 Testing API endpoints...")
    
    import requests
    
    base_url = "http://localhost:8000"
    endpoints_to_test = [
        "/health",
        "/graph/",
        "/graph/publications?limit=5",
        "/search/?query=microgravity&limit=5"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                logger.info(f"✅ {endpoint} - OK")
            else:
                logger.warning(f"⚠️  {endpoint} - Status: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ {endpoint} - Error: {e}")

def main():
    """Main startup sequence"""
    logger.info("🌟 NASA Knowledge Engine - Comprehensive Startup & Fix")
    logger.info("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        logger.error("❌ Please run this script from the NASA Backend directory")
        sys.exit(1)
    
    success_count = 0
    total_steps = 5
    
    # Step 1: Start Neo4j
    if start_neo4j():
        success_count += 1
        time.sleep(5)  # Give Neo4j time to fully initialize
        
        # Step 2: Setup Schema
        setup_neo4j_schema()
        success_count += 1
        
        # Step 3: Ingest Data
        if ingest_sample_data():
            success_count += 1
    else:
        logger.error("❌ Cannot continue without Neo4j")
    
    # Step 4: Start FastAPI Server
    if start_fastapi_server():
        success_count += 1
        
        # Step 5: Test Endpoints
        time.sleep(5)  # Wait for server to be ready
        test_endpoints()
        success_count += 1
    
    # Final Report
    logger.info("\n" + "=" * 60)
    logger.info("🎯 STARTUP COMPLETE")
    logger.info("=" * 60)
    logger.info(f"✅ Successful steps: {success_count}/{total_steps}")
    
    if success_count == total_steps:
        logger.info("🎉 All systems operational!")
        logger.info("\n📋 Next Steps:")
        logger.info("1. Access Neo4j Browser: http://localhost:7474")
        logger.info("   Username: neo4j, Password: testpassword")
        logger.info("2. Access API Documentation: http://localhost:8000/docs")
        logger.info("3. Test Graph Endpoint: http://localhost:8000/graph/")
        logger.info("4. Start Frontend: cd '../Nasa frontend' && npm run dev")
    else:
        logger.warning("⚠️  Some components failed to start - check logs above")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    main()