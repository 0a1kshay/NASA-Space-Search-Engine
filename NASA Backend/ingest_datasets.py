#!/usr/bin/env python3
"""
Master NASA Dataset Ingestion Coordinator
Orchestrates ingestion of all NASA data sources in proper sequence
"""

import sys
import os
import logging
import time
from datetime import datetime
from typing import Dict, Any, List
import asyncio

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import get_db
from ingest_publications import PublicationIngestion
from ingest_osdr import OSDRIngestion
from ingest_taskbook import TaskBookIngestion

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ingestion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MasterIngestion:
    """Coordinates all NASA data ingestion processes"""
    
    def __init__(self):
        self.db = get_db()
        self.start_time = datetime.now()
        self.stats = {
            'publications': {'processed': 0, 'errors': 0},
            'osdr_datasets': {'processed': 0, 'errors': 0},
            'taskbook_projects': {'processed': 0, 'errors': 0}
        }
        
    def setup_database_schema(self):
        """Apply Neo4j schema constraints and indexes"""
        logger.info("🔧 Setting up database schema...")
        
        if self.db.mock_mode:
            logger.warning("Database in mock mode - skipping schema setup")
            return True
        
        try:
            schema_file = os.path.join(os.path.dirname(__file__), 'schema.cypher')
            
            if not os.path.exists(schema_file):
                logger.warning(f"Schema file not found: {schema_file}")
                return False
            
            with open(schema_file, 'r') as f:
                schema_commands = f.read()
            
            # Split by semicolon and execute each command
            commands = [cmd.strip() for cmd in schema_commands.split(';') if cmd.strip()]
            
            with self.db.driver.session() as session:
                for cmd in commands:
                    if cmd.strip():
                        try:
                            session.run(cmd)
                            logger.debug(f"Executed: {cmd[:50]}...")
                        except Exception as e:
                            logger.warning(f"Schema command failed (may already exist): {e}")
            
            logger.info("✅ Database schema setup complete")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up database schema: {e}")
            return False
    
    def ingest_publications(self) -> bool:
        """Ingest publication data"""
        logger.info("📚 Starting publication data ingestion...")
        
        try:
            ingestion = PublicationIngestion()
            
            # Check if sample data exists
            sample_file = os.path.join(os.path.dirname(__file__), 'app', 'sample_data.json')
            if not os.path.exists(sample_file):
                logger.warning(f"Sample data file not found: {sample_file}")
                return False
            
            # Load and ingest publications
            publications = ingestion.load_sample_data()
            if publications:
                ingestion.ingest_batch(publications)
                stats = ingestion.get_stats()
                self.stats['publications'] = {
                    'processed': stats['processed_count'],
                    'errors': stats['error_count']
                }
                logger.info(f"✅ Publications ingestion complete: {stats['processed_count']} processed, {stats['error_count']} errors")
                return True
            else:
                logger.error("No publication data found")
                return False
                
        except Exception as e:
            logger.error(f"Publication ingestion failed: {e}")
            return False
    
    def ingest_osdr_datasets(self) -> bool:
        """Ingest OSDR dataset data"""
        logger.info("🛰️ Starting OSDR dataset ingestion...")
        
        try:
            ingestion = OSDRIngestion()
            
            # Fetch OSDR datasets
            datasets = ingestion.fetch_osdr_datasets()
            if datasets:
                ingestion.ingest_batch(datasets)
                stats = ingestion.get_stats()
                self.stats['osdr_datasets'] = {
                    'processed': stats['processed_count'],
                    'errors': stats['error_count']
                }
                logger.info(f"✅ OSDR datasets ingestion complete: {stats['processed_count']} processed, {stats['error_count']} errors")
                return True
            else:
                logger.error("No OSDR dataset data found")
                return False
                
        except Exception as e:
            logger.error(f"OSDR dataset ingestion failed: {e}")
            return False
    
    def ingest_taskbook_projects(self) -> bool:
        """Ingest Task Book project data"""
        logger.info("📋 Starting Task Book project ingestion...")
        
        try:
            ingestion = TaskBookIngestion()
            
            # Fetch Task Book projects
            projects = ingestion.fetch_taskbook_projects()
            if projects:
                ingestion.ingest_batch(projects)
                stats = ingestion.get_stats()
                self.stats['taskbook_projects'] = {
                    'processed': stats['processed_count'],
                    'errors': stats['error_count']
                }
                logger.info(f"✅ Task Book projects ingestion complete: {stats['processed_count']} processed, {stats['error_count']} errors")
                return True
            else:
                logger.error("No Task Book project data found")
                return False
                
        except Exception as e:
            logger.error(f"Task Book project ingestion failed: {e}")
            return False
    
    def run_full_ingestion(self, skip_schema: bool = False):
        """Run complete data ingestion pipeline"""
        logger.info("🚀 Starting complete NASA data ingestion pipeline...")
        
        success_count = 0
        total_steps = 4
        
        # Step 1: Setup database schema
        if not skip_schema:
            if self.setup_database_schema():
                success_count += 1
            else:
                logger.error("❌ Database schema setup failed")
        else:
            logger.info("⏭️ Skipping database schema setup")
            success_count += 1
        
        # Step 2: Ingest publications (foundation data)
        if self.ingest_publications():
            success_count += 1
        else:
            logger.error("❌ Publication ingestion failed")
        
        # Step 3: Ingest OSDR datasets
        if self.ingest_osdr_datasets():
            success_count += 1
        else:
            logger.error("❌ OSDR dataset ingestion failed")
        
        # Step 4: Ingest Task Book projects
        if self.ingest_taskbook_projects():
            success_count += 1
        else:
            logger.error("❌ Task Book project ingestion failed")
        
        self.print_final_report(success_count, total_steps)
    
    def print_final_report(self, success_count: int, total_steps: int):
        """Print comprehensive ingestion report"""
        duration = datetime.now() - self.start_time
        
        print("\n" + "="*80)
        print("🎯 NASA DATA INGESTION COMPLETE")
        print("="*80)
        print(f"⏱️  Total Duration: {duration}")
        print(f"✅ Successful Steps: {success_count}/{total_steps}")
        print()
        
        # Detailed statistics
        print("📊 DETAILED STATISTICS:")
        print("-" * 40)
        
        total_processed = 0
        total_errors = 0
        
        for data_type, stats in self.stats.items():
            processed = stats['processed']
            errors = stats['errors']
            total_processed += processed
            total_errors += errors
            
            status = "✅" if processed > 0 else "❌"
            print(f"{status} {data_type.title().replace('_', ' '):<20}: {processed:>4} processed, {errors:>2} errors")
        
        print("-" * 40)
        print(f"🎯 TOTAL                : {total_processed:>4} processed, {total_errors:>2} errors")
        
        if total_processed > 0:
            success_rate = (total_processed / (total_processed + total_errors)) * 100
            print(f"📈 Success Rate         : {success_rate:.1f}%")
        
        print()
        
        # Recommendations
        print("💡 NEXT STEPS:")
        print("- Verify data integrity with graph queries")
        print("- Test API endpoints for data retrieval")
        print("- Monitor database performance and indexes")
        print("- Set up automated data refresh schedules")
        
        if total_errors > 0:
            print("\n⚠️  ATTENTION: Some errors occurred during ingestion.")
            print("   Check ingestion.log for detailed error information.")
        
        print("="*80)


def main():
    """Main entry point"""
    print("🌟 NASA Space Biology Knowledge Engine - Data Ingestion Pipeline")
    print("=" * 80)
    
    # Parse command line arguments
    skip_schema = '--skip-schema' in sys.argv
    
    try:
        master = MasterIngestion()
        master.run_full_ingestion(skip_schema=skip_schema)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Ingestion interrupted by user")
        logger.info("Ingestion process interrupted by user")
        
    except Exception as e:
        print(f"\n\n❌ Fatal error during ingestion: {e}")
        logger.error(f"Fatal error during ingestion: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()