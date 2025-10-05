#!/usr/bin/env python3

from app.db import Neo4jDatabase
import os

def check_database_content():
    """Check what data exists in Neo4j database"""
    db = Neo4jDatabase()
    
    try:
        with db.driver.session() as session:
            print('=== CHECKING DATABASE CONTENT ===')
            result = session.run('MATCH (n) RETURN labels(n)[0] as type, count(n) as count ORDER BY type')
            for record in result:
                print(f'{record["type"]}: {record["count"]}')
            
            print('\n=== SAMPLE DATA ===')
            result = session.run('MATCH (n) RETURN n LIMIT 5')
            for i, record in enumerate(result):
                node = record['n']
                labels = list(node.labels)
                props = dict(node)
                print(f'Node {i+1}: {labels}')
                print(f'  Properties: {props}')
                print()
                
            print('=== RELATIONSHIPS ===')
            result = session.run('MATCH ()-[r]->() RETURN type(r) as rel_type, count(r) as count ORDER BY rel_type')
            for record in result:
                print(f'{record["rel_type"]}: {record["count"]}')
                
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == '__main__':
    check_database_content()