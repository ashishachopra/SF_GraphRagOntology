-- =====================================================
-- LAYER 1: PHYSICAL STORAGE LAYER
-- Universal node-and-edge model for the knowledge graph
-- =====================================================
USE DATABASE ONTOLOGY_DB;
USE SCHEMA DATA_KG;

-- =====================================================
-- KG_NODE: Entity storage table
-- Stores all entities (Customer, Account, Transaction, Device etc)
-- with flexible VARIANT properties
-- =====================================================
CREATE OR REPLACE TABLE KG_NODE (
    NODE_ID      STRING          NOT NULL,        -- stable global id
    NODE_TYPE    STRING          NOT NULL,        -- e.g., CUSTOMER | ACCOUNT | TRANSACTION | DEVICE
    NAME         STRING,                          -- common name attribute
    PROPS        VARIANT,                         -- type-specific JSON properties
    TS_INGESTED  TIMESTAMP_NTZ   DEFAULT CURRENT_TIMESTAMP(),
    CONSTRAINT PK_KG_NODE PRIMARY KEY (NODE_ID)
)
CLUSTER BY (NODE_TYPE);
COMMENT ON TABLE KG_NODE IS 'All entities (Customer, Account, Transaction, Device etc)';

-- =====================================================
-- KG_EDGE: Relationship storage table
-- Stores all relationships between entities with
-- temporal validity (effective start/end dates for products as necessary)
-- =====================================================
CREATE OR REPLACE TABLE KG_EDGE (
    EDGE_ID          STRING          NOT NULL,      -- can be a hash of (src, dst, type, start)
    SRC_ID           STRING          NOT NULL,
    DST_ID           STRING          NOT NULL,
    EDGE_TYPE        STRING          NOT NULL,      -- e.g., CUST_OWNS_PRODUCT | PRODUCT_TRANSACTIONS | CUSTOMER_TRANSACTIONS | CUSTOMER_DEVICE
    WEIGHT           FLOAT           DEFAULT 1.0,   -- relationship weight for graph algorithms
    PROPS            VARIANT,                       -- e.g., product_type, product_specific_attributes, device_type, device_specific_features, transaction_type, 										transaction_specific_attributes - customer grain,transaction_specific_attributes - product grain 
    EFFECTIVE_START  DATE,                          -- temporal validity start
    EFFECTIVE_END    DATE,                          -- temporal validity end (NULL = current)
    TS_INGESTED      TIMESTAMP_NTZ   DEFAULT CURRENT_TIMESTAMP(),
    CONSTRAINT PK_KG_EDGE PRIMARY KEY (EDGE_ID)
)
CLUSTER BY (EDGE_TYPE, SRC_ID, DST_ID);
COMMENT ON TABLE KG_EDGE IS 'All relationships between nodes; time-bounded where relevant.';