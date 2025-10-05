// Neo4j Schema for NASA Space Biology Knowledge Engine
// Run this file to create the database schema with proper constraints and indexes

// Create constraints for unique identifiers
CREATE CONSTRAINT publication_id IF NOT EXISTS FOR (p:Publication) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT dataset_id IF NOT EXISTS FOR (d:Dataset) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT project_id IF NOT EXISTS FOR (pr:Project) REQUIRE pr.id IS UNIQUE;
CREATE CONSTRAINT author_name IF NOT EXISTS FOR (a:Author) REQUIRE a.name IS UNIQUE;
CREATE CONSTRAINT organism_name IF NOT EXISTS FOR (o:Organism) REQUIRE o.name IS UNIQUE;
CREATE CONSTRAINT assay_name IF NOT EXISTS FOR (as:Assay) REQUIRE as.name IS UNIQUE;
CREATE CONSTRAINT mission_name IF NOT EXISTS FOR (m:Mission) REQUIRE m.name IS UNIQUE;
CREATE CONSTRAINT phenotype_name IF NOT EXISTS FOR (ph:Phenotype) REQUIRE ph.name IS UNIQUE;

// Create indexes for better query performance
CREATE INDEX publication_title IF NOT EXISTS FOR (p:Publication) ON (p.title);
CREATE INDEX publication_year IF NOT EXISTS FOR (p:Publication) ON (p.year);
CREATE INDEX author_affiliation IF NOT EXISTS FOR (a:Author) ON (a.affiliation);
CREATE INDEX dataset_organism IF NOT EXISTS FOR (d:Dataset) ON (d.organism);
CREATE INDEX project_pi IF NOT EXISTS FOR (pr:Project) ON (pr.pi);
CREATE INDEX project_funding IF NOT EXISTS FOR (pr:Project) ON (pr.funding_program);

// Full-text search indexes
CREATE FULLTEXT INDEX publication_search IF NOT EXISTS FOR (p:Publication) ON EACH [p.title, p.abstract];
CREATE FULLTEXT INDEX project_search IF NOT EXISTS FOR (pr:Project) ON EACH [pr.title, pr.description];

// Sample MERGE statements for data ingestion
// These will be used by the ingestion scripts

// Publication node template
// MERGE (p:Publication {id: $pub_id})
// SET p.title = $title,
//     p.year = $year,
//     p.doi = $doi,
//     p.url = $url,
//     p.abstract = $abstract,
//     p.created_at = datetime(),
//     p.updated_at = datetime()

// Dataset node template  
// MERGE (d:Dataset {id: $dataset_id})
// SET d.title = $title,
//     d.organism = $organism,
//     d.assay_type = $assay_type,
//     d.url = $url,
//     d.description = $description,
//     d.created_at = datetime(),
//     d.updated_at = datetime()

// Project node template
// MERGE (pr:Project {id: $project_id})
// SET pr.title = $title,
//     pr.pi = $pi,
//     pr.funding_program = $funding_program,
//     pr.start_date = $start_date,
//     pr.end_date = $end_date,
//     pr.description = $description,
//     pr.created_at = datetime(),
//     pr.updated_at = datetime()

// Author node template
// MERGE (a:Author {name: $author_name})
// SET a.affiliation = $affiliation,
//     a.email = $email,
//     a.orcid = $orcid,
//     a.created_at = datetime(),
//     a.updated_at = datetime()

// Relationship templates
// Publication to Author: (p:Publication)-[:AUTHORED_BY]->(a:Author)
// Publication to Dataset: (p:Publication)-[:USES]->(d:Dataset)  
// Publication to Organism: (p:Publication)-[:STUDIES]->(o:Organism)
// Publication to Assay: (p:Publication)-[:EMPLOYS]->(as:Assay)
// Publication to Mission: (p:Publication)-[:PART_OF]->(m:Mission)
// Publication to Phenotype: (p:Publication)-[:OBSERVES]->(ph:Phenotype)
// Project to Publication: (pr:Project)-[:FUNDED]->(p:Publication)
// Project to Dataset: (pr:Project)-[:GENERATED]->(d:Dataset)
// Dataset to Organism: (d:Dataset)-[:CONTAINS]->(o:Organism)
// Dataset to Assay: (d:Dataset)-[:USED_ASSAY]->(as:Assay)