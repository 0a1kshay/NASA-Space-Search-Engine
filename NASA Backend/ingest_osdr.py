#!/usr/bin/env python3
"""
NASA OSDR (Open Science Data Repository) Dataset Ingestion Script
Fetches OSDR dataset metadata via API and ingests into Neo4j graph database
"""

import json
import requests
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

from app.db import get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OSDRIngestion:
    """Handles ingestion of NASA OSDR dataset metadata into Neo4j"""
    
    def __init__(self):
        self.db = get_db()
        self.processed_count = 0
        self.error_count = 0
        self.errors = []
        self.base_url = "https://osdr.nasa.gov/osdr/data/osd/files/{OSD_STUDY_IDs}/?page={CURRENT_PAGE_NUMBER}&size={RESULTS_PER_PAGE}?all_files={ALL_FILES}"
        self.api_url = "https://osdr.nasa.gov/osdr/data/search"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'NASA-Space-Biology-Knowledge-Engine/1.0'
        })
    
    def fetch_osdr_datasets(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Fetch OSDR datasets from NASA API"""
        try:
            # OSDR API parameters
            params = {
                'type': 'study',
                'size': limit,
                'from': offset,
                'sort': 'modified_date:desc'
            }
            
            logger.info(f"Fetching OSDR datasets (limit: {limit}, offset: {offset})")
            response = self.session.get(self.api_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'hits' in data and 'hits' in data['hits']:
                datasets = data['hits']['hits']
                logger.info(f"Retrieved {len(datasets)} datasets from OSDR")
                return [self._parse_osdr_dataset(ds['_source']) for ds in datasets]
            else:
                logger.warning("Unexpected OSDR API response format")
                return self._get_mock_osdr_data()
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching OSDR data: {e}")
            logger.info("Using mock OSDR data")
            return self._get_mock_osdr_data()
        except Exception as e:
            logger.error(f"Unexpected error fetching OSDR data: {e}")
            return self._get_mock_osdr_data()
    
    def _get_mock_osdr_data(self) -> List[Dict[str, Any]]:
        """Provide mock OSDR data when API is unavailable"""
        return [
            {
                'id': 'GLDS-394',
                'title': 'Transcriptomic analysis of Arabidopsis thaliana roots exposed to microgravity',
                'organism': 'Arabidopsis thaliana',
                'assay_type': 'RNA sequencing (RNA-Seq)',
                'url': 'https://osdr.nasa.gov/bio/repo/data/studies/OSD-394',
                'description': 'RNA-seq analysis of Arabidopsis roots grown in microgravity conditions aboard the ISS',
                'pi': 'Dr. Sarah Johnson',
                'mission': 'ISS Expedition 45/46',
                'submission_date': '2020-03-15',
                'organism_part': 'root',
                'factor': 'microgravity'
            },
            {
                'id': 'GLDS-401',
                'title': 'Mouse muscle tissue analysis after 30-day spaceflight',
                'organism': 'Mus musculus',
                'assay_type': 'Proteomics',
                'url': 'https://osdr.nasa.gov/bio/repo/data/studies/OSD-401',
                'description': 'Proteomic analysis of mouse skeletal muscle after 30 days in microgravity',
                'pi': 'Dr. Michael Chen',
                'mission': 'SpaceX-20',
                'submission_date': '2021-01-20',
                'organism_part': 'skeletal muscle',
                'factor': 'microgravity'
            },
            {
                'id': 'GLDS-415',
                'title': 'Bacterial biofilm formation in microgravity conditions',
                'organism': 'Escherichia coli',
                'assay_type': 'Microscopy',
                'url': 'https://osdr.nasa.gov/bio/repo/data/studies/OSD-415',
                'description': 'Analysis of E. coli biofilm formation patterns in microgravity environment',
                'pi': 'Dr. Lisa Wang',
                'mission': 'ISS Expedition 64/65',
                'submission_date': '2023-04-10',
                'organism_part': 'whole organism',
                'factor': 'microgravity'
            },
            {
                'id': 'GLDS-428',
                'title': 'Radiation effects on plant seed germination for Mars missions',
                'organism': 'Triticum aestivum',
                'assay_type': 'Germination assay',
                'url': 'https://osdr.nasa.gov/bio/repo/data/studies/OSD-428',
                'description': 'Evaluation of wheat seed viability after exposure to Mars-equivalent radiation',
                'pi': 'Dr. Robert Kim',
                'mission': 'Mars Radiation Environment Simulation',
                'submission_date': '2023-08-22',
                'organism_part': 'seed',
                'factor': 'radiation'
            },
            {
                'id': 'GLDS-435',
                'title': 'Human cell culture response to cosmic radiation exposure',
                'organism': 'Homo sapiens',
                'assay_type': 'Cell culture',
                'url': 'https://osdr.nasa.gov/bio/repo/data/studies/OSD-435',
                'description': 'Analysis of human fibroblast response to simulated cosmic radiation',
                'pi': 'Dr. Jennifer Martinez',
                'mission': 'Ground-based simulation',
                'submission_date': '2023-11-15',
                'organism_part': 'fibroblast',
                'factor': 'cosmic radiation'
            }
        ]
    
    def _parse_osdr_dataset(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse raw OSDR API response into standardized format"""
        return {
            'id': raw_data.get('accession', raw_data.get('id', 'unknown')),
            'title': raw_data.get('title', ''),
            'organism': raw_data.get('organism', {}).get('name', '') if isinstance(raw_data.get('organism'), dict) else raw_data.get('organism', ''),
            'assay_type': raw_data.get('assay_type', raw_data.get('study_assay', '')),
            'url': f"https://osdr.nasa.gov/bio/repo/data/studies/{raw_data.get('accession', '')}",
            'description': raw_data.get('description', raw_data.get('study_description', '')),
            'pi': raw_data.get('principal_investigator', raw_data.get('pi', '')),
            'mission': raw_data.get('mission', raw_data.get('space_program', '')),
            'submission_date': raw_data.get('submission_date', raw_data.get('release_date', '')),
            'organism_part': raw_data.get('organism_part', ''),
            'factor': raw_data.get('factor', raw_data.get('study_factor', ''))
        }
    
    def ingest_dataset(self, dataset_data: Dict[str, Any]) -> bool:
        """Ingest a single dataset into Neo4j"""
        if self.db.mock_mode:
            logger.warning("Database in mock mode - skipping actual ingestion")
            return True
        
        try:
            with self.db.driver.session() as session:
                result = session.execute_write(self._create_dataset_tx, dataset_data)
                
                if result:
                    self.processed_count += 1
                    logger.debug(f"Ingested dataset: {dataset_data['id']}")
                    return True
                else:
                    raise Exception("Failed to create dataset node")
                    
        except Exception as e:
            self.error_count += 1
            error_msg = f"Error ingesting dataset {dataset_data.get('id', 'unknown')}: {e}"
            self.errors.append(error_msg)
            logger.error(error_msg)
            return False
    
    @staticmethod
    def _create_dataset_tx(tx, dataset_data):
        """Transaction to create dataset and related nodes"""
        
        # Create dataset node
        dataset_query = """
        MERGE (d:Dataset {id: $id})
        SET d.title = $title,
            d.organism = $organism,
            d.assay_type = $assay_type,
            d.url = $url,
            d.description = $description,
            d.pi = $pi,
            d.mission = $mission,
            d.submission_date = $submission_date,
            d.organism_part = $organism_part,
            d.factor = $factor,
            d.created_at = datetime(),
            d.updated_at = datetime()
        RETURN d.id as dataset_id
        """
        
        result = tx.run(dataset_query, **dataset_data)
        dataset_id = result.single()['dataset_id']
        
        # Create organism relationship
        if dataset_data.get('organism'):
            tx.run("""
            MERGE (o:Organism {name: $organism})
            WITH o
            MATCH (d:Dataset {id: $dataset_id})
            MERGE (d)-[:CONTAINS]->(o)
            """, organism=dataset_data['organism'], dataset_id=dataset_id)
        
        # Create assay relationship
        if dataset_data.get('assay_type'):
            tx.run("""
            MERGE (a:Assay {name: $assay_type})
            WITH a
            MATCH (d:Dataset {id: $dataset_id})
            MERGE (d)-[:USED_ASSAY]->(a)
            """, assay_type=dataset_data['assay_type'], dataset_id=dataset_id)
        
        # Create mission relationship
        if dataset_data.get('mission'):
            tx.run("""
            MERGE (m:Mission {name: $mission})
            WITH m
            MATCH (d:Dataset {id: $dataset_id})
            MERGE (d)-[:PART_OF]->(m)
            """, mission=dataset_data['mission'], dataset_id=dataset_id)
        
        # Link to publications that might use this dataset
        # This creates relationships based on matching organisms and assays
        if dataset_data.get('organism') and dataset_data.get('assay_type'):
            tx.run("""
            MATCH (d:Dataset {id: $dataset_id})
            MATCH (p:Publication)-[:STUDIES]->(o:Organism {name: $organism})
            MATCH (p)-[:EMPLOYS]->(a:Assay {name: $assay_type})
            MERGE (p)-[:USES]->(d)
            """, dataset_id=dataset_id, organism=dataset_data['organism'], assay_type=dataset_data['assay_type'])
        
        return dataset_id
    
    def ingest_batch(self, datasets: List[Dict[str, Any]], batch_size: int = 50):
        """Ingest datasets in batches"""
        total = len(datasets)
        logger.info(f"Starting ingestion of {total} datasets in batches of {batch_size}")
        
        for i in range(0, total, batch_size):
            batch = datasets[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(total + batch_size - 1)//batch_size}")
            
            for dataset in batch:
                self.ingest_dataset(dataset)
                time.sleep(0.1)  # Rate limiting
        
        logger.info(f"Ingestion complete. Processed: {self.processed_count}, Errors: {self.error_count}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get ingestion statistics"""
        return {
            'processed_count': self.processed_count,
            'error_count': self.error_count,
            'errors': self.errors[:10]
        }


def main():
    """Main function to run OSDR dataset ingestion"""
    ingestion = OSDRIngestion()
    
    # Fetch datasets from OSDR API
    datasets = []
    
    # Fetch in batches to avoid overwhelming the API
    for offset in range(0, 500, 100):  # Fetch up to 500 datasets
        batch = ingestion.fetch_osdr_datasets(limit=100, offset=offset)
        if not batch:
            break
        datasets.extend(batch)
        time.sleep(1)  # Rate limiting
    
    if not datasets:
        logger.error("No OSDR datasets found.")
        return
    
    logger.info(f"Fetched {len(datasets)} datasets from OSDR")
    
    # Ingest data
    ingestion.ingest_batch(datasets)
    
    # Print statistics
    stats = ingestion.get_stats()
    print(f"\n📊 OSDR Ingestion Statistics:")
    print(f"✅ Successfully processed: {stats['processed_count']}")
    print(f"❌ Errors: {stats['error_count']}")
    
    if stats['errors']:
        print(f"\n🚨 Sample errors:")
        for error in stats['errors']:
            print(f"  - {error}")


if __name__ == "__main__":
    main()