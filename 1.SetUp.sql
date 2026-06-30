-- =====================================================
-- ONTOLOGY ON SNOWFLAKE - SETUP SCRIPT
-- Creates database and schema for the knowledge graph
-- =====================================================

-- Create database
CREATE OR REPLACE DATABASE ONTOLOGY_DB;
USE DATABASE ONTOLOGY_DB;

-- Create schema
CREATE OR REPLACE SCHEMA DATA_KG;
USE SCHEMA DATA_KG;

-- Grant Privilages
GRANT USAGE ON DATABASE ONTOLOGY_DB TO ROLE <SFLK_GBU_A01A0E_DEVELOPER_DEV>;
GRANT USAGE ON SCHEMA ONTOLOGY_DB.DATA_KG TO ROLE <SFLK_GBU_A01A0E_DEVELOPER_DEV>;

COMMENT ON DATABASE ONTOLOGY_DB IS 'Ontology on Snowflake - Data Knowledge Graph';
COMMENT ON SCHEMA DATA_KG IS 'Knowledge graph with ontology metadata layer';