import os
import json
import sys
from dotenv import load_dotenv

# Add the project root to path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import Neo4jDatabase

# Sample data for seeding the database
SAMPLE_DATA = [
    {
        "id": "pub001",
        "title": "Effects of Microgravity on Arabidopsis thaliana Gene Expression",
        "authors": ["Smith, J.A.", "Johnson, M.B.", "Williams, R.T."],
        "year": 2020,
        "url": "https://example.com/pub001",
        "abstract": "This study investigates the effects of microgravity on gene expression patterns in Arabidopsis thaliana during the ISS expedition 45/46. Results show significant changes in genes related to cell wall integrity and auxin signaling.",
        "organisms": ["Arabidopsis thaliana"],
        "assays": ["RNA-Seq", "qPCR"],
        "phenotypes": ["Altered root development", "Reduced lignin content"],
        "missions": ["ISS Expedition 45/46"]
    },
    {
        "id": "pub002",
        "title": "Bone Density Changes in Mice After Long-term Spaceflight",
        "authors": ["Brown, L.K.", "Davis, S.P.", "Taylor, A.M."],
        "year": 2021,
        "url": "https://example.com/pub002",
        "abstract": "This research examines the impact of extended exposure to microgravity on bone density in mice during the SpaceX-20 mission. Findings indicate significant bone loss that was partially recovered upon return to Earth.",
        "organisms": ["Mus musculus"],
        "assays": ["micro-CT scan", "Histology"],
        "phenotypes": ["Bone density loss", "Altered osteoclast activity"],
        "missions": ["SpaceX-20"]
    },
    {
        "id": "pub003",
        "title": "Comparative Analysis of Human and Rodent Muscle Atrophy in Space",
        "authors": ["Garcia, M.R.", "Patel, S.K.", "Roberts, T.V."],
        "year": 2022,
        "url": "https://example.com/pub003",
        "abstract": "This comparative study analyzes muscle atrophy patterns between human astronauts and rodent models during spaceflight. Results suggest conserved molecular pathways but different magnitudes of effect across species.",
        "organisms": ["Homo sapiens", "Mus musculus", "Rattus norvegicus"],
        "assays": ["Proteomics", "Muscle biopsy", "Grip strength test"],
        "phenotypes": ["Muscle atrophy", "Reduced myofibril density"],
        "missions": ["ISS Expedition 52/53", "SpaceX-20"]
    },
    {
        "id": "pub004",
        "title": "Altered Bacterial Growth Patterns in Microgravity Environment",
        "authors": ["Zhang, W.Q.", "Morales, J.L.", "Kostov, Y.V."],
        "year": 2023,
        "url": "https://example.com/pub004",
        "abstract": "This investigation documents the growth patterns and biofilm formation of Escherichia coli and Bacillus subtilis aboard the ISS. Microgravity conditions were found to enhance biofilm formation and alter antibiotic resistance profiles.",
        "organisms": ["Escherichia coli", "Bacillus subtilis"],
        "assays": ["Bacterial culture", "Biofilm assay", "Antibiotic susceptibility testing"],
        "phenotypes": ["Enhanced biofilm formation", "Altered antibiotic resistance"],
        "missions": ["ISS Expedition 64/65"]
    },
    {
        "id": "pub005",
        "title": "Radiation Exposure Effects on Plant Seed Viability for Mars Missions",
        "authors": ["Kim, S.J.", "Alvarez, R.M.", "Petrov, D.N."],
        "year": 2023,
        "url": "https://example.com/pub005",
        "abstract": "This research evaluates the effects of Mars-equivalent radiation exposure on seed viability across five crop species. Results indicate species-specific radiation tolerance with implications for future Mars mission agriculture planning.",
        "organisms": ["Triticum aestivum", "Solanum lycopersicum", "Lactuca sativa", "Raphanus sativus", "Glycine max"],
        "assays": ["Germination assay", "Radiation exposure simulation", "DNA damage assessment"],
        "phenotypes": ["Reduced germination rate", "Chromosomal aberrations", "Delayed development"],
        "missions": ["Mars Radiation Environment Simulation"]
    }
]


def seed_database():
    """Seed the database with sample publications"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Create database connection
        db = Neo4jDatabase()
        
        print(f"Connected to Neo4j database")
        print(f"Seeding database with {len(SAMPLE_DATA)} sample publications...")
        
        # Create each publication
        for pub_data in SAMPLE_DATA:
            db.create_publication(pub_data)
            print(f"Created publication: {pub_data['id']} - {pub_data['title']}")
        
        print("Database seeding completed successfully")
        
        # Close database connection
        db.close()
        
    except Exception as e:
        print(f"Error seeding database: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    seed_database()