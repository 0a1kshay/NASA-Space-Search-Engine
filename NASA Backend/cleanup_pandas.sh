#!/bin/bash
# 🔧 Pandas Cleanup Script for NASA Backend
# Temporarily renames pandas-dependent files to prevent import errors

echo "🧹 Cleaning up pandas-dependent files..."

# Backup pandas-dependent files
if [ -f "form_scraper.py" ]; then
    mv "form_scraper.py" "form_scraper.py.backup"
    echo "✅ Backed up form_scraper.py"
fi

if [ -f "ingest_publications.py" ]; then
    mv "ingest_publications.py" "ingest_publications.py.backup"
    echo "✅ Backed up ingest_publications.py"
fi

# Create lightweight replacements
echo "🔄 Creating lightweight alternatives..."

cat > form_scraper_lite.py << 'EOF'
"""
Lightweight form scraper - pandas-free version
"""
import logging
logger = logging.getLogger(__name__)

def scrape_nasa_forms():
    """Placeholder - implement with pure Python if needed"""
    logger.info("Form scraper disabled (pandas-free mode)")
    return []
EOF

cat > ingest_publications_lite.py << 'EOF'
"""
Lightweight publications ingestion - pandas-free version
"""
import csv
import logging
logger = logging.getLogger(__name__)

def ingest_publications_csv(file_path: str):
    """Lightweight CSV ingestion using pure Python"""
    try:
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            publications = list(reader)
            logger.info(f"✅ Ingested {len(publications)} publications")
            return publications
    except Exception as e:
        logger.error(f"❌ Failed to ingest publications: {e}")
        return []
EOF

echo "✅ Pandas cleanup complete - backend is now pandas-free!"