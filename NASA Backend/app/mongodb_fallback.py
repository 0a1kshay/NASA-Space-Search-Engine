"""
MongoDB fallback implementation for Space Biology Knowledge Engine.

This module provides MongoDB implementations of the database operations
for projects where Neo4j might be too resource-intensive.

To use this implementation:
1. Uncomment the MongoDB imports and comment out Neo4j imports in the project
2. Update the .env file with MongoDB connection details
3. Replace Neo4jDatabase class with MongoDBDatabase in db.py

Example .env for MongoDB:
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=space_biology
"""

from dotenv import load_dotenv
import os
import logging
import json
from pymongo import MongoClient
from bson.objectid import ObjectId

# Load environment variables from .env file
load_dotenv()

# Configure logger
logger = logging.getLogger(__name__)


class MongoDBDatabase:
    """MongoDB database connection and query handler"""
    
    def __init__(self):
        """Initialize MongoDB database connection"""
        uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        db_name = os.getenv("MONGODB_DB", "space_biology")
        
        try:
            self.client = MongoClient(uri)
            self.db = self.client[db_name]
            # Create collections
            self.publications = self.db["publications"]
            self.organisms = self.db["organisms"]
            self.assays = self.db["assays"]
            self.phenotypes = self.db["phenotypes"]
            self.missions = self.db["missions"]
            
            # Create indexes for faster queries
            self.publications.create_index("title")
            self.organisms.create_index("name")
            self.assays.create_index("name")
            self.phenotypes.create_index("name")
            self.missions.create_index("name")
            
            logger.info("Connected to MongoDB database")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise ConnectionError(f"Failed to connect to MongoDB: {str(e)}")
    
    def close(self):
        """Close the database connection"""
        if self.client:
            self.client.close()
    
    def create_publication(self, publication_data):
        """Create a publication document and its relationships"""
        try:
            # Store publication document
            pub_id = publication_data.get("id")
            pub_doc = {
                "id": pub_id,
                "title": publication_data.get("title"),
                "authors": publication_data.get("authors", []),
                "year": publication_data.get("year"),
                "url": publication_data.get("url", ""),
                "abstract": publication_data.get("abstract", ""),
                "organisms": [],
                "assays": [],
                "phenotypes": [],
                "missions": []
            }
            
            # Create organism relationships
            if "organisms" in publication_data and publication_data["organisms"]:
                for organism in publication_data["organisms"]:
                    # Create or update organism document
                    self.organisms.update_one(
                        {"name": organism},
                        {"$set": {"name": organism}, 
                         "$addToSet": {"publications": pub_id}},
                        upsert=True
                    )
                    pub_doc["organisms"].append(organism)
            
            # Create assay relationships
            if "assays" in publication_data and publication_data["assays"]:
                for assay in publication_data["assays"]:
                    # Create or update assay document
                    self.assays.update_one(
                        {"name": assay},
                        {"$set": {"name": assay}, 
                         "$addToSet": {"publications": pub_id}},
                        upsert=True
                    )
                    pub_doc["assays"].append(assay)
            
            # Create phenotype relationships
            if "phenotypes" in publication_data and publication_data["phenotypes"]:
                for phenotype in publication_data["phenotypes"]:
                    # Create or update phenotype document
                    self.phenotypes.update_one(
                        {"name": phenotype},
                        {"$set": {"name": phenotype}, 
                         "$addToSet": {"publications": pub_id}},
                        upsert=True
                    )
                    pub_doc["phenotypes"].append(phenotype)
            
            # Create mission relationships
            if "missions" in publication_data and publication_data["missions"]:
                for mission in publication_data["missions"]:
                    # Create or update mission document
                    self.missions.update_one(
                        {"name": mission},
                        {"$set": {"name": mission}, 
                         "$addToSet": {"publications": pub_id}},
                        upsert=True
                    )
                    pub_doc["missions"].append(mission)
            
            # Insert publication
            self.publications.insert_one(pub_doc)
            
            return pub_id
        except Exception as e:
            logger.error(f"Error creating publication: {str(e)}")
            raise
    
    def get_full_graph(self):
        """Get the full knowledge graph data"""
        try:
            # Get all publications with their relationships
            publications = list(self.publications.find({}, {"_id": 0}))
            
            # Format for frontend visualization
            nodes = {}
            edges = []
            
            # Add publication nodes
            for pub in publications:
                pub_id = pub["id"]
                nodes[pub_id] = {
                    "id": pub_id,
                    "label": pub["title"],
                    "type": "Publication"
                }
                
                # Add organism relationships
                for organism in pub.get("organisms", []):
                    node_id = f"Organism_{organism}"
                    if node_id not in nodes:
                        nodes[node_id] = {
                            "id": node_id,
                            "label": organism,
                            "type": "Organism"
                        }
                    edges.append({
                        "source": pub_id,
                        "target": node_id,
                        "label": "STUDIES"
                    })
                
                # Add assay relationships
                for assay in pub.get("assays", []):
                    node_id = f"Assay_{assay}"
                    if node_id not in nodes:
                        nodes[node_id] = {
                            "id": node_id,
                            "label": assay,
                            "type": "Assay"
                        }
                    edges.append({
                        "source": pub_id,
                        "target": node_id,
                        "label": "USES"
                    })
                
                # Add phenotype relationships
                for phenotype in pub.get("phenotypes", []):
                    node_id = f"Phenotype_{phenotype}"
                    if node_id not in nodes:
                        nodes[node_id] = {
                            "id": node_id,
                            "label": phenotype,
                            "type": "Phenotype"
                        }
                    edges.append({
                        "source": pub_id,
                        "target": node_id,
                        "label": "OBSERVES"
                    })
                
                # Add mission relationships
                for mission in pub.get("missions", []):
                    node_id = f"Mission_{mission}"
                    if node_id not in nodes:
                        nodes[node_id] = {
                            "id": node_id,
                            "label": mission,
                            "type": "Mission"
                        }
                    edges.append({
                        "source": pub_id,
                        "target": node_id,
                        "label": "PART_OF"
                    })
            
            return {
                "nodes": list(nodes.values()),
                "edges": edges
            }
        except Exception as e:
            logger.error(f"Error retrieving graph data: {str(e)}")
            raise
    
    def get_node_details(self, node_id):
        """Get detailed information about a node"""
        try:
            # Check if it's a publication
            pub = self.publications.find_one({"id": node_id}, {"_id": 0})
            
            if pub:
                return {
                    "type": "Publication",
                    "details": pub
                }
            
            # Check if it's another type of node (Organism, Assay, etc.)
            if "_" in node_id:
                node_type, name = node_id.split("_", 1)
                
                # Get entity document
                collection = getattr(self, node_type.lower() + "s")
                entity = collection.find_one({"name": name}, {"_id": 0})
                
                if entity:
                    # Get related publications
                    pub_ids = entity.get("publications", [])
                    publications = list(self.publications.find(
                        {"id": {"$in": pub_ids}},
                        {"_id": 0, "id": 1, "title": 1, "year": 1}
                    ))
                    
                    return {
                        "type": node_type,
                        "details": {
                            "name": entity["name"],
                            "publications": publications
                        }
                    }
            
            return None
        except Exception as e:
            logger.error(f"Error retrieving node details: {str(e)}")
            raise
    
    def search_publications(self, query):
        """Search for publications matching the query"""
        try:
            query_lower = query.lower()
            
            # Search in publications
            publications = list(self.publications.find({
                "$or": [
                    {"title": {"$regex": query_lower, "$options": "i"}},
                    {"abstract": {"$regex": query_lower, "$options": "i"}},
                    {"organisms": {"$regex": query_lower, "$options": "i"}},
                    {"assays": {"$regex": query_lower, "$options": "i"}},
                    {"phenotypes": {"$regex": query_lower, "$options": "i"}},
                    {"missions": {"$regex": query_lower, "$options": "i"}}
                ]
            }, {"_id": 0}))
            
            return publications
        except Exception as e:
            logger.error(f"Error searching publications: {str(e)}")
            raise
    
    def compare_publications(self, pub_id1, pub_id2):
        """Compare two publications"""
        try:
            pub1 = self.publications.find_one({"id": pub_id1}, {"_id": 0})
            pub2 = self.publications.find_one({"id": pub_id2}, {"_id": 0})
            
            if not pub1 or not pub2:
                return None
                
            # Find common and unique elements
            common_organisms = list(set(pub1.get("organisms", [])) & set(pub2.get("organisms", [])))
            common_assays = list(set(pub1.get("assays", [])) & set(pub2.get("assays", [])))
            common_phenotypes = list(set(pub1.get("phenotypes", [])) & set(pub2.get("phenotypes", [])))
            common_missions = list(set(pub1.get("missions", [])) & set(pub2.get("missions", [])))
            
            pub1_unique_organisms = list(set(pub1.get("organisms", [])) - set(pub2.get("organisms", [])))
            pub2_unique_organisms = list(set(pub2.get("organisms", [])) - set(pub1.get("organisms", [])))
            
            pub1_unique_assays = list(set(pub1.get("assays", [])) - set(pub2.get("assays", [])))
            pub2_unique_assays = list(set(pub2.get("assays", [])) - set(pub1.get("assays", [])))
            
            pub1_unique_phenotypes = list(set(pub1.get("phenotypes", [])) - set(pub2.get("phenotypes", [])))
            pub2_unique_phenotypes = list(set(pub2.get("phenotypes", [])) - set(pub1.get("phenotypes", [])))
            
            pub1_unique_missions = list(set(pub1.get("missions", [])) - set(pub2.get("missions", [])))
            pub2_unique_missions = list(set(pub2.get("missions", [])) - set(pub1.get("missions", [])))
            
            return {
                "publication1": {
                    "id": pub1["id"],
                    "title": pub1["title"],
                    "year": pub1["year"],
                    "unique_organisms": pub1_unique_organisms,
                    "unique_assays": pub1_unique_assays,
                    "unique_phenotypes": pub1_unique_phenotypes,
                    "unique_missions": pub1_unique_missions
                },
                "publication2": {
                    "id": pub2["id"],
                    "title": pub2["title"],
                    "year": pub2["year"],
                    "unique_organisms": pub2_unique_organisms,
                    "unique_assays": pub2_unique_assays,
                    "unique_phenotypes": pub2_unique_phenotypes,
                    "unique_missions": pub2_unique_missions
                },
                "common": {
                    "organisms": common_organisms,
                    "assays": common_assays,
                    "phenotypes": common_phenotypes,
                    "missions": common_missions
                }
            }
        except Exception as e:
            logger.error(f"Error comparing publications: {str(e)}")
            raise