#!/usr/bin/env python3
"""
NASA Publications Data Ingestion Script
Loads publications from CSV/JSON and ingests them into Neo4j graph database
"""

import json
import csv
import os
import logging
from typing import List, Dict, Any
from datetime import datetime
import pandas as pd

from app.db import get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PublicationIngestion:
    """Handles ingestion of NASA publication data into Neo4j"""
    
    def __init__(self):
        self.db = get_db()
        self.processed_count = 0
        self.error_count = 0
        self.errors = []
    
    def load_from_json(self, file_path: str) -> List[Dict[str, Any]]:
        """Load publications from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded {len(data)} publications from {file_path}")
            return data
        except Exception as e:
            logger.error(f"Error loading JSON file {file_path}: {e}")
            return []
    
    def load_from_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """Load publications from CSV file"""
        try:
            df = pd.read_csv(file_path)
            
            # Map CSV columns to our schema
            publications = []
            for _, row in df.iterrows():
                pub = {
                    'id': f"pub_{row.get('id', len(publications) + 1):03d}",
                    'title': row.get('title', ''),
                    'year': int(row.get('year', 0)) if pd.notna(row.get('year')) else None,
                    'url': row.get('url', row.get('link', '')),
                    'doi': row.get('doi', ''),
                    'abstract': row.get('abstract', ''),
                    'authors': self._parse_authors(row.get('authors', '')),
                    'organisms': self._parse_list_field(row.get('organisms', '')),
                    'assays': self._parse_list_field(row.get('assays', '')),
                    'phenotypes': self._parse_list_field(row.get('phenotypes', '')),
                    'missions': self._parse_list_field(row.get('missions', ''))
                }
                publications.append(pub)
            
            logger.info(f"Loaded {len(publications)} publications from CSV")
            return publications
            
        except Exception as e:
            logger.error(f"Error loading CSV file {file_path}: {e}")
            return []
    
    def _parse_authors(self, authors_str: str) -> List[str]:
        """Parse authors string into list"""
        if not authors_str or pd.isna(authors_str):
            return []
        
        # Handle different author formats
        if authors_str.startswith('[') and authors_str.endswith(']'):
            # JSON-like format
            try:
                return json.loads(authors_str.replace("'", '"'))
            except:
                pass
        
        # Comma-separated format
        return [author.strip() for author in authors_str.split(',') if author.strip()]
    
    def _parse_list_field(self, field_str: str) -> List[str]:
        """Parse list field from string"""
        if not field_str or pd.isna(field_str):
            return []
        
        if field_str.startswith('[') and field_str.endswith(']'):
            try:
                return json.loads(field_str.replace("'", '"'))
            except:
                pass
        
        return [item.strip() for item in field_str.split(',') if item.strip()]
    
    def ingest_publication(self, pub_data: Dict[str, Any]) -> bool:
        """Ingest a single publication into Neo4j"""
        if self.db.mock_mode:
            logger.warning("Database in mock mode - skipping actual ingestion")
            return True
        
        try:
            with self.db.driver.session() as session:
                # Create publication node
                result = session.execute_write(self._create_publication_tx, pub_data)
                
                if result:
                    self.processed_count += 1
                    logger.debug(f"Ingested publication: {pub_data['title'][:50]}...")
                    return True
                else:
                    raise Exception("Failed to create publication node")
                    
        except Exception as e:
            self.error_count += 1
            error_msg = f"Error ingesting publication {pub_data.get('id', 'unknown')}: {e}"
            self.errors.append(error_msg)
            logger.error(error_msg)
            return False
    
    @staticmethod
    def _create_publication_tx(tx, pub_data):
        """Transaction to create publication and related nodes"""
        
        # Create publication node
        pub_query = """
        MERGE (p:Publication {id: $id})
        SET p.title = $title,
            p.year = $year,
            p.url = $url,
            p.doi = $doi,
            p.abstract = $abstract,
            p.created_at = datetime(),
            p.updated_at = datetime()
        RETURN p.id as pub_id
        """
        
        result = tx.run(pub_query, 
                       id=pub_data['id'],
                       title=pub_data['title'],
                       year=pub_data.get('year'),
                       url=pub_data.get('url', ''),
                       doi=pub_data.get('doi', ''),
                       abstract=pub_data.get('abstract', ''))
        
        pub_id = result.single()['pub_id']
        
        # Create author relationships
        for author_name in pub_data.get('authors', []):
            tx.run("""
            MERGE (a:Author {name: $name})
            WITH a
            MATCH (p:Publication {id: $pub_id})
            MERGE (p)-[:AUTHORED_BY]->(a)
            """, name=author_name, pub_id=pub_id)
        
        # Create organism relationships
        for organism in pub_data.get('organisms', []):
            tx.run("""
            MERGE (o:Organism {name: $name})
            WITH o
            MATCH (p:Publication {id: $pub_id})
            MERGE (p)-[:STUDIES]->(o)
            """, name=organism, pub_id=pub_id)
        
        # Create assay relationships
        for assay in pub_data.get('assays', []):
            tx.run("""
            MERGE (a:Assay {name: $name})
            WITH a
            MATCH (p:Publication {id: $pub_id})
            MERGE (p)-[:EMPLOYS]->(a)
            """, name=assay, pub_id=pub_id)
        
        # Create phenotype relationships
        for phenotype in pub_data.get('phenotypes', []):
            tx.run("""
            MERGE (ph:Phenotype {name: $name})
            WITH ph
            MATCH (p:Publication {id: $pub_id})
            MERGE (p)-[:OBSERVES]->(ph)
            """, name=phenotype, pub_id=pub_id)
        
        # Create mission relationships
        for mission in pub_data.get('missions', []):
            tx.run("""
            MERGE (m:Mission {name: $name})
            WITH m
            MATCH (p:Publication {id: $pub_id})
            MERGE (p)-[:PART_OF]->(m)
            """, name=mission, pub_id=pub_id)
        
        return pub_id
    
    def ingest_batch(self, publications: List[Dict[str, Any]], batch_size: int = 100):
        """Ingest publications in batches"""
        total = len(publications)
        logger.info(f"Starting ingestion of {total} publications in batches of {batch_size}")
        
        for i in range(0, total, batch_size):
            batch = publications[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(total + batch_size - 1)//batch_size}")
            
            for pub in batch:
                self.ingest_publication(pub)
        
        logger.info(f"Ingestion complete. Processed: {self.processed_count}, Errors: {self.error_count}")
        
        if self.errors:
            logger.info("First 5 errors:")
            for error in self.errors[:5]:
                logger.error(error)
    
    def load_sample_data(self) -> List[Dict[str, Any]]:
        """Load sample data from app/sample_data.json"""
        sample_data_file = os.path.join('app', 'sample_data.json')
        
        if os.path.exists(sample_data_file):
            return self.load_from_json(sample_data_file)
        else:
            logger.warning(f"Sample data file not found: {sample_data_file}, using mock data")
            return self._get_mock_publications()
    
    def _get_mock_publications(self) -> List[Dict[str, Any]]:
        """Provide mock publication data when files are not available"""
        return [
            {
                'id': 'pub_001',
                'title': 'Effects of Microgravity on Arabidopsis Root Development and Gene Expression',
                'authors': ['Dr. Sarah Martinez', 'Dr. Michael Chen', 'Dr. Emily Rodriguez'],
                'year': 2023,
                'url': 'https://www.nasa.gov/science/biological/publications/arabidopsis-microgravity-2023',
                'doi': '10.1016/j.spaceres.2023.001',
                'abstract': 'This study investigates the molecular mechanisms underlying root development in Arabidopsis thaliana under microgravity conditions. We performed RNA-seq analysis on root samples from plants grown on the International Space Station.',
                'organisms': ['Arabidopsis thaliana'],
                'assays': ['RNA Sequencing', 'Microscopy'],
                'phenotypes': ['Root Growth', 'Gene Expression'],
                'missions': ['ISS Expedition 68']
            },
            {
                'id': 'pub_002',
                'title': 'Radiation Effects on Mouse Muscle Tissue During Spaceflight',
                'authors': ['Dr. Robert Kim', 'Dr. Lisa Wang', 'Dr. David Brown'],
                'year': 2023,
                'url': 'https://www.nasa.gov/science/biological/publications/mouse-radiation-2023',
                'doi': '10.1016/j.spaceres.2023.002',
                'abstract': 'Investigation of radiation-induced changes in mouse skeletal muscle during long-duration spaceflight missions.',
                'organisms': ['Mus musculus'],
                'assays': ['Proteomics', 'Histology'],
                'phenotypes': ['Muscle Atrophy', 'Protein Expression'],
                'missions': ['SpaceX CRS-26']
            },
            {
                'id': 'pub_003',
                'title': 'Microbial Biofilm Formation in Microgravity Environments',
                'authors': ['Dr. Jennifer Martinez', 'Dr. Alex Petrov'],
                'year': 2022,
                'url': 'https://www.nasa.gov/science/biological/publications/biofilm-microgravity-2022',
                'doi': '10.1016/j.spaceres.2022.003',
                'abstract': 'Analysis of bacterial biofilm architecture and antibiotic resistance patterns in microgravity conditions.',
                'organisms': ['Escherichia coli', 'Staphylococcus aureus'],
                'assays': ['Microscopy', 'Growth Assays'],
                'phenotypes': ['Biofilm Formation', 'Antibiotic Resistance'],
                'missions': ['ISS National Lab']
            },
            {
                'id': 'pub_004',
                'title': 'Plant Cell Wall Modifications in Response to Space Environment',
                'authors': ['Dr. Maria Gonzalez', 'Dr. Thomas Anderson'],
                'year': 2024,
                'url': 'https://www.nasa.gov/science/biological/publications/cell-wall-space-2024',
                'doi': '10.1016/j.spaceres.2024.001',
                'abstract': 'Comprehensive analysis of cell wall biosynthesis and structural modifications in plants exposed to space conditions.',
                'organisms': ['Arabidopsis thaliana', 'Solanum lycopersicum'],
                'assays': ['Cell Wall Analysis', 'Immunohistochemistry'],
                'phenotypes': ['Cell Wall Thickness', 'Cellulose Content'],
                'missions': ['Artemis Research']
            },
            {
                'id': 'pub_005',
                'title': 'Cardiovascular Deconditioning Countermeasures in Astronauts',
                'authors': ['Dr. Rachel Green', 'Dr. Kevin Wu', 'Dr. Anna Rodriguez'],
                'year': 2023,
                'url': 'https://www.nasa.gov/science/biological/publications/cardiovascular-countermeasures-2023',
                'doi': '10.1016/j.spaceres.2023.005',
                'abstract': 'Evaluation of exercise protocols and pharmaceutical interventions for preventing cardiovascular deconditioning during long-duration spaceflight.',
                'organisms': ['Homo sapiens'],
                'assays': ['Echocardiography', 'Blood Analysis'],
                'phenotypes': ['Cardiac Function', 'Blood Pressure'],
                'missions': ['ISS Long Duration Missions']
            }
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get ingestion statistics"""
        return {
            'processed_count': self.processed_count,
            'error_count': self.error_count,
            'errors': self.errors[:10]  # Return first 10 errors
        }


def main():
    """Main function to run publication ingestion"""
    ingestion = PublicationIngestion()
    
    # Check for data files
    sample_data_file = 'app/sample_data.json'
    csv_data_file = 'data/publications.csv'  # Expected CSV file location
    
    publications = []
    
    # Load from JSON sample data
    if os.path.exists(sample_data_file):
        publications.extend(ingestion.load_from_json(sample_data_file))
    
    # Load from CSV if available
    if os.path.exists(csv_data_file):
        publications.extend(ingestion.load_from_csv(csv_data_file))
    
    if not publications:
        logger.error("No publication data found. Please ensure data files exist.")
        return
    
    # Remove duplicates based on ID
    unique_pubs = {pub['id']: pub for pub in publications}
    publications = list(unique_pubs.values())
    
    # Ingest data
    ingestion.ingest_batch(publications)
    
    # Print statistics
    stats = ingestion.get_stats()
    print(f"\n📊 Ingestion Statistics:")
    print(f"✅ Successfully processed: {stats['processed_count']}")
    print(f"❌ Errors: {stats['error_count']}")
    
    if stats['errors']:
        print(f"\n🚨 Sample errors:")
        for error in stats['errors']:
            print(f"  - {error}")


if __name__ == "__main__":
    main()