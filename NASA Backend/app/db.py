from dotenv import load_dotenv
import os
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError
import logging
import time

# Load environment variables from .env file
load_dotenv()

# Configure logger
logger = logging.getLogger(__name__)

class Neo4jDatabase:
    """Neo4j database connection and query handler"""
    
    def __init__(self):
        """Initialize Neo4j database connection"""
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "testpassword")
        
        logger.info(f"Attempting to connect to Neo4j at {uri}")
        
        self.driver = None
        self.mock_mode = True
        
        # Try connecting with retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Use modern Neo4j 5+ connection approach
                self.driver = GraphDatabase.driver(
                    uri, 
                    auth=(user, password),
                    max_connection_lifetime=30 * 60,  # 30 minutes
                    max_connection_pool_size=50,
                    connection_acquisition_timeout=60
                )
                
                # Verify connection with proper error handling
                with self.driver.session() as session:
                    result = session.run("RETURN 1 as test")
                    test_value = result.single()["test"]
                    if test_value == 1:
                        logger.info("✅ Connected to Neo4j database successfully")
                        self.mock_mode = False
                        break
                
            except ServiceUnavailable as e:
                logger.warning(f"Neo4j service unavailable (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)  # Wait 5 seconds before retry
                    
            except AuthError as e:
                logger.error(f"Neo4j authentication failed: {e}")
                break
                
            except Exception as e:
                logger.warning(f"Failed to connect to Neo4j (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
        
        if self.mock_mode:
            logger.warning("⚠️  Using mock mode - Neo4j not available")
            self.driver = None
    
    def close(self):
        """Close the database connection"""
        if self.driver:
            self.driver.close()
    
    def create_publication(self, publication_data):
        """Create a publication node and its relationships"""
        with self.driver.session() as session:
            return session.execute_write(self._create_publication_tx, publication_data)
    
    @staticmethod
    def _create_publication_tx(tx, publication_data):
        """Transaction function to create a publication with relationships"""
        # Create publication node
        query = """
        CREATE (p:Publication {
            id: $id,
            title: $title,
            authors: $authors,
            year: $year,
            url: $url,
            abstract: $abstract
        })
        RETURN p.id as id
        """
        
        result = tx.run(query, 
                      id=publication_data.get("id"),
                      title=publication_data.get("title"),
                      authors=publication_data.get("authors", []),
                      year=publication_data.get("year"),
                      url=publication_data.get("url", ""),
                      abstract=publication_data.get("abstract", ""))
        
        publication_id = result.single()["id"]
        
        # Create organism relationships
        if "organisms" in publication_data and publication_data["organisms"]:
            for organism in publication_data["organisms"]:
                tx.run("""
                MERGE (o:Organism {name: $name})
                WITH o
                MATCH (p:Publication {id: $pub_id})
                CREATE (p)-[:STUDIES]->(o)
                """, name=organism, pub_id=publication_id)
        
        # Create assay relationships
        if "assays" in publication_data and publication_data["assays"]:
            for assay in publication_data["assays"]:
                tx.run("""
                MERGE (a:Assay {name: $name})
                WITH a
                MATCH (p:Publication {id: $pub_id})
                CREATE (p)-[:USES]->(a)
                """, name=assay, pub_id=publication_id)
        
        # Create phenotype relationships
        if "phenotypes" in publication_data and publication_data["phenotypes"]:
            for phenotype in publication_data["phenotypes"]:
                tx.run("""
                MERGE (ph:Phenotype {name: $name})
                WITH ph
                MATCH (p:Publication {id: $pub_id})
                CREATE (p)-[:OBSERVES]->(ph)
                """, name=phenotype, pub_id=publication_id)
        
        # Create mission relationships
        if "missions" in publication_data and publication_data["missions"]:
            for mission in publication_data["missions"]:
                tx.run("""
                MERGE (m:Mission {name: $name})
                WITH m
                MATCH (p:Publication {id: $pub_id})
                CREATE (p)-[:PART_OF]->(m)
                """, name=mission, pub_id=publication_id)
        
        return publication_id
    
    def get_full_graph(self):
        """Get the full knowledge graph data"""
        if self.mock_mode:
            return self._get_mock_graph()
        
        try:
            with self.driver.session() as session:
                return session.execute_read(self._get_full_graph_tx)
        except Exception as e:
            logger.error(f"Error getting graph data: {e}")
            return self._get_mock_graph()
    
    @staticmethod
    def _get_full_graph_tx(tx):
        """Transaction function to get full graph data"""
        try:
            # Get all nodes first
            nodes_query = """
            MATCH (n)
            RETURN id(n) as internal_id, 
                   COALESCE(n.id, n.name) as node_id,
                   COALESCE(n.title, n.name, 'Unknown') as label,
                   labels(n)[0] as type,
                   COALESCE(n.description, n.abstract, '') as description
            LIMIT 200
            """
            
            nodes_result = tx.run(nodes_query)
            nodes = {}
            id_mapping = {}
            
            for record in nodes_result:
                internal_id = record["internal_id"]
                node_id = record["node_id"] or f"node_{internal_id}"
                
                nodes[node_id] = {
                    "id": node_id,
                    "label": record["label"][:50] + "..." if len(record["label"]) > 50 else record["label"],
                    "type": record["type"],
                    "description": record["description"][:100] + "..." if len(record["description"]) > 100 else record["description"]
                }
                
                id_mapping[internal_id] = node_id
            
            # Get relationships
            edges_query = """
            MATCH (a)-[r]->(b)
            RETURN id(a) as source_internal, id(b) as target_internal, type(r) as rel_type
            LIMIT 500
            """
            
            edges_result = tx.run(edges_query)
            edges = []
            
            for record in edges_result:
                source_id = id_mapping.get(record["source_internal"])
                target_id = id_mapping.get(record["target_internal"])
                
                if source_id and target_id and source_id in nodes and target_id in nodes:
                    edges.append({
                        "source": source_id,
                        "target": target_id,
                        "type": record["rel_type"]
                    })
            
            return {
                "nodes": list(nodes.values()),
                "edges": edges
            }
            
        except Exception as e:
            logger.error(f"Error in graph transaction: {e}")
            # Return empty graph if query fails
            return {"nodes": [], "edges": []}
    
    def get_node_details(self, node_id):
        """Get detailed information about a node"""
        if self.mock_mode:
            return self._get_mock_node_details(node_id)
        with self.driver.session() as session:
            return session.execute_read(self._get_node_details_tx, node_id)
    
    @staticmethod
    def _get_node_details_tx(tx, node_id):
        """Transaction function to get node details"""
        # First check if it's a publication
        query = """
        MATCH (p:Publication {id: $node_id})
        RETURN p {.id, .title, .authors, .year, .url, .abstract} AS details,
               'Publication' AS type
        """
        result = tx.run(query, node_id=node_id)
        record = result.single()
        
        if record:
            details = record["details"]
            
            # Get related entities for publications
            organisms_query = """
            MATCH (p:Publication {id: $node_id})-[:STUDIES]->(o:Organism)
            RETURN collect(o.name) AS organisms
            """
            organisms = tx.run(organisms_query, node_id=node_id).single()["organisms"]
            
            assays_query = """
            MATCH (p:Publication {id: $node_id})-[:USES]->(a:Assay)
            RETURN collect(a.name) AS assays
            """
            assays = tx.run(assays_query, node_id=node_id).single()["assays"]
            
            phenotypes_query = """
            MATCH (p:Publication {id: $node_id})-[:OBSERVES]->(ph:Phenotype)
            RETURN collect(ph.name) AS phenotypes
            """
            phenotypes = tx.run(phenotypes_query, node_id=node_id).single()["phenotypes"]
            
            missions_query = """
            MATCH (p:Publication {id: $node_id})-[:PART_OF]->(m:Mission)
            RETURN collect(m.name) AS missions
            """
            missions = tx.run(missions_query, node_id=node_id).single()["missions"]
            
            # Add related entities to details
            details["organisms"] = organisms
            details["assays"] = assays
            details["phenotypes"] = phenotypes
            details["missions"] = missions
            
            return {"type": "Publication", "details": details}
        
        # Check if it's another type of node (Organism, Assay, etc.)
        # Parse the node_id to get type and name (TypeName_Value format)
        if "_" in node_id:
            node_type, name = node_id.split("_", 1)
            
            # Get all publications related to this entity
            query = f"""
            MATCH (p:Publication)-[r]->(n:{node_type} {{name: $name}})
            RETURN n.name AS name, collect(p {{.id, .title, .year}}) AS publications
            """
            
            result = tx.run(query, name=name)
            record = result.single()
            
            if record:
                return {
                    "type": node_type,
                    "details": {
                        "name": record["name"],
                        "publications": record["publications"]
                    }
                }
        
        return None
    
    def search_publications(self, query):
        """Search for publications matching the query"""
        if self.mock_mode:
            return self._get_mock_search_results(query)
        try:
            with self.driver.session() as session:
                return session.execute_read(self._search_publications_tx, query)
        except Exception as e:
            logger.error(f"Error searching publications: {e}")
            return self._get_mock_search_results(query)
    
    def search_publications_advanced(self, search_params):
        """Advanced search with filters and sorting"""
        if self.mock_mode:
            return self._get_mock_search_results(search_params.get('query', ''))
        
        try:
            with self.driver.session() as session:
                return session.execute_read(self._search_publications_advanced_tx, search_params)
        except Exception as e:
            logger.error(f"Error in advanced search: {e}")
            return []
    
    @staticmethod
    def _search_publications_tx(tx, query):
        """Transaction function to search for publications"""
        try:
            # Convert query to lowercase for case-insensitive search
            query_lower = f"(?i).*{query}.*"
            
            search_query = """
            MATCH (p:Publication)
            WHERE p.title =~ $query_pattern OR p.abstract =~ $query_pattern
            RETURN p {.id, .title, .year, .url, .abstract} AS publication
            LIMIT 50
            
            UNION
            
            MATCH (p:Publication)-[:STUDIES]->(o:Organism)
            WHERE o.name =~ $query_pattern
            RETURN p {.id, .title, .year, .url, .abstract} AS publication
            LIMIT 50
            
            UNION
            
            MATCH (p:Publication)-[:EMPLOYS]->(a:Assay)
            WHERE a.name =~ $query_pattern
            RETURN p {.id, .title, .year, .url, .abstract} AS publication
            LIMIT 50
            
            UNION
            
            MATCH (p:Publication)-[:OBSERVES]->(ph:Phenotype)
            WHERE ph.name =~ $query_pattern
            RETURN p {.id, .title, .year, .url, .abstract} AS publication
            LIMIT 50
            
            UNION
            
            MATCH (p:Publication)-[:PART_OF]->(m:Mission)
            WHERE m.name =~ $query_pattern
            RETURN p {.id, .title, .year, .url, .abstract} AS publication
            LIMIT 50
            """
            
            result = tx.run(search_query, query_pattern=query_lower)
            publications = [record["publication"] for record in result]
            
            # Remove duplicates (same publication may match multiple criteria)
            unique_publications = {}
            for pub in publications:
                if pub and pub.get("id"):
                    pub_id = pub["id"]
                    if pub_id not in unique_publications:
                        unique_publications[pub_id] = pub
            
            return list(unique_publications.values())
            
        except Exception as e:
            logger.error(f"Error in search transaction: {e}")
            return []
    
    @staticmethod
    def _search_publications_advanced_tx(tx, search_params):
        """Advanced search transaction with filters"""
        try:
            search_query = search_params.get('query', '')
            missions = search_params.get('missions', [])
            content_types = search_params.get('content_types', [])
            tags = search_params.get('tags', [])
            authors = search_params.get('authors', [])
            date_filter = search_params.get('date_filter')
            limit = search_params.get('limit', 50)
            
            # Start building the Cypher query
            if content_types:
                # Handle different content types
                results = []
                
                if 'research-papers' in content_types:
                    # Get publications
                    pub_query = "MATCH (p:Publication) "
                    pub_where = []
                    pub_params = {}
                    
                    if search_query:
                        pub_where.append("(p.title CONTAINS $search_text OR p.abstract CONTAINS $search_text)")
                        pub_params['search_text'] = search_query
                    
                    if missions:
                        pub_query += "-[:PART_OF]->(m:Mission) "
                        pub_where.append("m.name IN $mission_list")
                        pub_params['mission_list'] = missions
                    
                    if date_filter and date_filter.get('start') and date_filter.get('end'):
                        pub_where.append("p.year >= $start_year AND p.year <= $end_year")
                        pub_params['start_year'] = int(date_filter['start'])
                        pub_params['end_year'] = int(date_filter['end'])
                    
                    if pub_where:
                        pub_query += "WHERE " + " AND ".join(pub_where) + " "
                    
                    pub_query += """
                    RETURN p.id as id, p.title as title, 'research-papers' as type, 
                           p.year as date, p.abstract as abstract, p.url as url,
                           'Research Papers' as content_type
                    ORDER BY p.year DESC
                    LIMIT $limit
                    """
                    pub_params['limit'] = limit
                    
                    pub_result = tx.run(pub_query, pub_params)
                    results.extend([dict(record) for record in pub_result])
                
                if 'osdr-data' in content_types:
                    # Get datasets
                    ds_query = "MATCH (d:Dataset) "
                    ds_where = []
                    ds_params = {}
                    
                    if search_query:
                        ds_where.append("(d.title CONTAINS $search_text OR d.description CONTAINS $search_text)")
                        ds_params['search_text'] = search_query
                    
                    if ds_where:
                        ds_query += "WHERE " + " AND ".join(ds_where) + " "
                    
                    ds_query += """
                    RETURN d.id as id, d.title as title, 'osdr-data' as type,
                           d.description as abstract, d.url as url,
                           'OSDR Data' as content_type, 2023 as date
                    ORDER BY d.title
                    LIMIT $limit
                    """
                    ds_params['limit'] = limit
                    
                    ds_result = tx.run(ds_query, ds_params)
                    results.extend([dict(record) for record in ds_result])
                
                if 'task-book-grants' in content_types:
                    # Get projects
                    proj_query = "MATCH (pr:Project) "
                    proj_where = []
                    proj_params = {}
                    
                    if search_query:
                        proj_where.append("(pr.title CONTAINS $search_text OR pr.description CONTAINS $search_text)")
                        proj_params['search_text'] = search_query
                    
                    if proj_where:
                        proj_query += "WHERE " + " AND ".join(proj_where) + " "
                    
                    proj_query += """
                    RETURN pr.id as id, pr.title as title, 'task-book-grants' as type,
                           pr.description as abstract, '' as url,
                           'Task Book Grants' as content_type, 2023 as date
                    ORDER BY pr.title
                    LIMIT $limit
                    """
                    proj_params['limit'] = limit
                    
                    proj_result = tx.run(proj_query, proj_params)
                    results.extend([dict(record) for record in proj_result])
                
                return results
                
            else:
                # Default search across all types
                search_query_cypher = """
                MATCH (p:Publication)
                WHERE ($search_text = '' OR p.title CONTAINS $search_text OR p.abstract CONTAINS $search_text)
                RETURN p.id as id, p.title as title, 'research-papers' as type,
                       p.year as date, p.abstract as abstract, p.url as url,
                       'Research Papers' as content_type
                ORDER BY p.year DESC
                LIMIT $limit
                
                UNION ALL
                
                MATCH (d:Dataset)
                WHERE ($search_text = '' OR d.title CONTAINS $search_text OR d.description CONTAINS $search_text)
                RETURN d.id as id, d.title as title, 'osdr-data' as type,
                       2023 as date, d.description as abstract, d.url as url,
                       'OSDR Data' as content_type
                ORDER BY d.title
                LIMIT $limit
                
                UNION ALL
                
                MATCH (pr:Project)
                WHERE ($search_text = '' OR pr.title CONTAINS $search_text OR pr.description CONTAINS $search_text)
                RETURN pr.id as id, pr.title as title, 'task-book-grants' as type,
                       2023 as date, pr.description as abstract, '' as url,
                       'Task Book Grants' as content_type
                ORDER BY pr.title
                LIMIT $limit
                """
                
                params = {
                    'search_text': search_query,
                    'limit': limit
                }
                
                result = tx.run(search_query_cypher, params)
                return [dict(record) for record in result]
            
        except Exception as e:
            logger.error(f"Error in advanced search transaction: {e}")
            return []
    
    def compare_publications(self, pub_id1, pub_id2):
        """Compare two publications"""
        with self.driver.session() as session:
            pub1 = session.execute_read(self._get_node_details_tx, pub_id1)
            pub2 = session.execute_read(self._get_node_details_tx, pub_id2)
            
            if not pub1 or not pub2:
                return None
                
            # Extract details
            pub1_details = pub1["details"]
            pub2_details = pub2["details"]
            
            # Find common and unique elements
            common_organisms = list(set(pub1_details["organisms"]) & set(pub2_details["organisms"]))
            common_assays = list(set(pub1_details["assays"]) & set(pub2_details["assays"]))
            common_phenotypes = list(set(pub1_details["phenotypes"]) & set(pub2_details["phenotypes"]))
            common_missions = list(set(pub1_details["missions"]) & set(pub2_details["missions"]))
            
            pub1_unique_organisms = list(set(pub1_details["organisms"]) - set(pub2_details["organisms"]))
            pub2_unique_organisms = list(set(pub2_details["organisms"]) - set(pub1_details["organisms"]))
            
            pub1_unique_assays = list(set(pub1_details["assays"]) - set(pub2_details["assays"]))
            pub2_unique_assays = list(set(pub2_details["assays"]) - set(pub1_details["assays"]))
            
            pub1_unique_phenotypes = list(set(pub1_details["phenotypes"]) - set(pub2_details["phenotypes"]))
            pub2_unique_phenotypes = list(set(pub2_details["phenotypes"]) - set(pub1_details["phenotypes"]))
            
            pub1_unique_missions = list(set(pub1_details["missions"]) - set(pub2_details["missions"]))
            pub2_unique_missions = list(set(pub2_details["missions"]) - set(pub1_details["missions"]))
            
            return {
                "publication1": {
                    "id": pub1_details["id"],
                    "title": pub1_details["title"],
                    "year": pub1_details["year"],
                    "unique_organisms": pub1_unique_organisms,
                    "unique_assays": pub1_unique_assays,
                    "unique_phenotypes": pub1_unique_phenotypes,
                    "unique_missions": pub1_unique_missions
                },
                "publication2": {
                    "id": pub2_details["id"],
                    "title": pub2_details["title"],
                    "year": pub2_details["year"],
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

    # Mock data methods for when Neo4j is not available
    def _get_mock_graph(self):
        """Return mock graph data when Neo4j is not available"""
        return {
            "nodes": [
                {"id": "pub_123", "label": "Effects of Microgravity on Plant Growth", "type": "Publication"},
                {"id": "org_arabidopsis", "label": "Arabidopsis", "type": "Organism"},
                {"id": "assay_rna_seq", "label": "RNA Sequencing", "type": "Assay"},
                {"id": "phenotype_root_growth", "label": "Root Growth", "type": "Phenotype"},
                {"id": "mission_iss", "label": "International Space Station", "type": "Mission"}
            ],
            "edges": [
                {"source": "pub_123", "target": "org_arabidopsis", "label": "STUDIES"},
                {"source": "pub_123", "target": "assay_rna_seq", "label": "USES"},
                {"source": "pub_123", "target": "phenotype_root_growth", "label": "OBSERVES"},
                {"source": "pub_123", "target": "mission_iss", "label": "PART_OF"}
            ]
        }

    def _get_mock_search_results(self, query):
        """Return mock search results when Neo4j is not available"""
        return [
            {
                "id": "pub_123",
                "title": "Effects of Microgravity on Plant Cell Wall Formation and Root Growth",
                "authors": ["Dr. Sarah Martinez", "Dr. Chen Liu", "Dr. Robert Anderson"],
                "year": 2024,
                "url": "https://example.com/publication/123",
                "abstract": "This comprehensive study investigates how microgravity environments affect cellular development in Arabidopsis roots, with implications for sustainable agriculture during long-duration space missions to Mars."
            }
        ]

    def _get_mock_node_details(self, node_id):
        """Return mock node details when Neo4j is not available"""
        if node_id == "pub_123":
            return {
                "type": "Publication",
                "details": {
                    "id": "pub_123",
                    "title": "Effects of Microgravity on Plant Cell Wall Formation and Root Growth",
                    "authors": ["Dr. Sarah Martinez", "Dr. Chen Liu", "Dr. Robert Anderson"],
                    "year": 2024,
                    "url": "https://example.com/publication/123",
                    "abstract": "This comprehensive study investigates how microgravity environments affect cellular development in Arabidopsis roots."
                }
            }
        elif "org_" in node_id:
            return {
                "type": "Organism",
                "details": {
                    "name": "Arabidopsis",
                    "publications": [
                        {"id": "pub_123", "title": "Effects of Microgravity on Plant Growth", "year": 2024}
                    ]
                }
            }
        return None


# Create a singleton database instance
neo4j_db = None

def get_db():
    """Get or create the Neo4j database connection"""
    global neo4j_db
    if neo4j_db is None:
        neo4j_db = Neo4jDatabase()
    return neo4j_db