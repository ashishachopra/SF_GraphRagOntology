-- =====================================================
-- SEED DATA: ONTOLOGY METADATA
-- Populates the ontology metadata tables
-- =====================================================

USE DATABASE ONTOLOGY_DB;
USE SCHEMA DATA_KG;

-- =====================================================
-- ONTOLOGY REGISTRY
-- =====================================================
INSERT INTO ONT_ONTOLOGY (ONTOLOGY_NAME, VERSION, DESCRIPTION, DEFAULT_SCHEMA, CREATED_BY, IS_ACTIVE)
VALUES ('DATA_V1', '1.0.0', 'Knowledge Graph Ontology', 'DATA_KG', 'SYSTEM', TRUE);

-- =====================================================
-- SHARED PROPERTIES
-- Reusable property definitions across classes
-- =====================================================
INSERT INTO ONT_SHARED_PROPERTY (SHARED_PROP_NAME, BASE_TYPE, DESCRIPTION, DEFAULT_FORMAT) VALUES
('identity', 'STRING', 'Unique identifier for any entity', NULL),
('entityrelationdt_start', 'DATE', 'Start date for time-bounded entities', 'YYYY-MM-DD'),
('entityrelationdt_end', 'DATE', 'End date for time-bounded entities', 'YYYY-MM-DD'),
('name', 'STRING', 'Display name', NULL),
('transaction', 'STRING', 'transaction key', NULL),

-- =====================================================
-- ABSTRACT CLASSES
-- =====================================================
INSERT INTO ONT_CLASS (CLASS_NAME, PARENT_CLASS_NAME, IS_ABSTRACT, DESCRIPTION, ONTOLOGY_NAME, TYPE_CLASS, STATUS) VALUES
('Thing', NULL, TRUE, 'Root class for all entities', 'DATA_V1', 'ABSTRACT', 'ACTIVE'),
('Customer', 'Thing', TRUE, 'Any customer', 'DATA_V1', 'ABSTRACT', 'ACTIVE'),
('Account', 'Thing', TRUE, 'Any product', 'DATA_V1', 'ABSTRACT', 'ACTIVE'),
('Device', 'Thing', TRUE, 'Any device', 'DATA_V1', 'ABSTRACT', 'ACTIVE'),
('Transaction', 'Thing', TRUE, 'Any transaction', 'DATA_V1', 'ABSTRACT', 'ACTIVE');

-- =====================================================
-- CONCRETE CLASSES
-- =====================================================
INSERT INTO ONT_CLASS (CLASS_NAME, PARENT_CLASS_NAME, IS_ABSTRACT, DESCRIPTION, ONTOLOGY_NAME, TYPE_CLASS, STATUS) VALUES
('Customer', 'Customer', FALSE, 'customer', 'DATA_V1', 'OPERATIONAL', 'ACTIVE'),
('Account', 'Account', FALSE, 'product', 'DATA_V1', 'OPERATIONAL', 'ACTIVE'),
('Device', 'Device', FALSE, 'device', 'DATA_V1', 'OPERATIONAL', 'ACTIVE')
('Transaction', 'Transaction', TRUE, 'transaction', 'DATA_V1', 'ABSTRACT', 'ACTIVE');

-- =====================================================
-- CLASS PROPERTIES
-- setup as entity_views.props.datatypes
-- =====================================================
-- Customer properties
INSERT INTO ONT_PROPERTY (CLASS_NAME, PROP_NAME, DATA_TYPE, SHARED_PROP_NAME, IS_REQUIRED, IS_INDEXED, DESCRIPTION) VALUES
('Customer', 'name', 'STRING', 'name', TRUE, TRUE, 'Full name of the customer'),
('Customer', 'customertype', 'STRING', 'customertype', TRUE, TRUE, 'customer type'),
('Customer', 'nationality', 'STRING', 'nationality', TRUE, TRUE, 'nationality'),
('Customer', 'birthdate', 'DATE', 'birthdate', TRUE, TRUE, 'birthdate'),
('Customer', 'email', 'STRING', 'email', TRUE, TRUE, 'email'),
('Customer', 'phonenumber', 'STRING', 'phonenumber', TRUE, TRUE, 'phonenumber'),
('Customer', 'address', 'STRING', 'address', TRUE, TRUE, 'address');

-- Product properties
INSERT INTO ONT_PROPERTY (CLASS_NAME, PROP_NAME, DATA_TYPE, SHARED_PROP_NAME, IS_REQUIRED, IS_INDEXED, DESCRIPTION) VALUES
('Account', 'name', 'STRING', 'name', TRUE, TRUE, 'Full name of the customer'),
('Account', 'accounttype', 'STRING', 'accounttype', TRUE, TRUE, 'account type'),
('Account', 'primarycustomer', 'STRING', 'primarycustomer', TRUE, TRUE, 'primary customer'),
('Account', 'opendate', 'DATE', 'opendate', TRUE, TRUE, 'open date'),
('Account', 'closeddate', 'DATE', 'closeddate', TRUE, TRUE, 'closed date'),
('Account', 'accountbalance', 'INTEGER', 'accountbalance', TRUE, TRUE, 'account balance'),
('Account', 'relationshipmanager', 'STRING', 'relationshipmanager', TRUE, TRUE, 'relationship manager');

-- Device properties
INSERT INTO ONT_PROPERTY (CLASS_NAME, PROP_NAME, DATA_TYPE, SHARED_PROP_NAME, IS_REQUIRED, IS_INDEXED, DESCRIPTION) VALUES
('Device', 'name', 'STRING', 'name', TRUE, TRUE, 'Full name of the customer'),
('Device', 'devicetype', 'STRING', 'devicetype', TRUE, TRUE, 'device type'),
('Device', 'imeinumber', 'STRING', 'imeinumber', TRUE, TRUE, 'imeinumber'),
('Device', 'version', 'INTEGER', 'version', TRUE, TRUE, 'version'),
('Device', 'phonenumber', 'STRING', 'phonenumber', TRUE, TRUE, 'phone number'),
('Device', 'primarycustomer', 'STRING', 'primarycustomer', TRUE, TRUE, 'primary customer');

-- Transaction properties
INSERT INTO ONT_PROPERTY (CLASS_NAME, PROP_NAME, DATA_TYPE, SHARED_PROP_NAME, IS_REQUIRED, IS_INDEXED, DESCRIPTION) VALUES
('Transaction', 'txndate', 'DATE', 'txndate', TRUE, TRUE, 'txn date'),
('Transaction', 'amount', 'INTEGER', 'amount', TRUE, TRUE, 'amount'),
('Transaction', 'basecurrency', 'STRING', 'basecurrency', TRUE, TRUE, 'base currency'),
('Transaction', 'actualcurrency', 'STRING', 'actualcurrency', TRUE, TRUE, 'actual currency'),
('Transaction', 'creditdebit', 'INTEGER', 'creditdebit', TRUE, TRUE, 'credit debit'),
('Transaction', 'primarycustomer', 'STRING', 'primarycustomer', TRUE, TRUE, 'primary customer'),
('Transaction', 'account', 'STRING', 'account', TRUE, TRUE, 'account'),
('Transaction', 'device', 'STRING', 'device', FALSE, TRUE, 'device'),;

-- =====================================================
-- RELATIONSHIP DEFINITIONS
-- setup as relationship_views
-- =====================================================
INSERT INTO ONT_RELATION_DEF (REL_NAME, DOMAIN_CLASS, RANGE_CLASS, CARDINALITY, IS_HIERARCHICAL, INVERSE_REL_NAME, DESCRIPTION, ONTOLOGY_NAME, STATUS, RENDER_HINT) VALUES
-- Abstract relationships ('<NOTHING ABSTRACT NOW>', 'Customer', 'Account', 'N:N', FALSE, 'owns', 'Customer owns product', 'DATA_V1', 'ACTIVE', 'directed'),

-- Concrete relationships
('CUST_OWNS_PRODUCT', 'Account', 'Customer', 'N:N', FALSE, 'ACC_HAS_CUST', 'Customer Account Link', 'DATA_V1', 'ACTIVE', 'directed'),
('PRODUCT_TRANSACTIONS', 'Account', 'Transaction', '1:1', FALSE, 'ACC_HAS_TXN', 'Account on which Transactions done', 'DATA_V1', 'ACTIVE', 'directed'),
('CUSTOMER_TRANSACTIONS', 'Customer', 'Transaction', '1:1', FALSE, 'CUST_HAS_TXN', 'Customer who did the tarnsaction', 'DATA_V1', 'ACTIVE', 'directed'),
('CUSTOMER_DEVICE', 'Device', 'Customer', '1:1', FALSE, 'DEVICE_CUST_OWNS', 'Device owned by Customer', 'DATA_V1', 'ACTIVE', 'directed');

-- =======================================
-- CLASS MAPPINGS (Abstract -> Concrete)
-- setup as entity_views
-- =======================================
INSERT INTO ONT_CLASS_MAP (CLASS_NAME, CONCRETE_VIEW, ID_COL, SUBTYPE_VALUE) VALUES
('Customer', 'V_CUSTOMER', 'NODE_ID', 'Customer'),
('Account', 'V_ACCOUNT', 'NODE_ID', 'Account'),
('Transaction', 'V_TRANSACTION', 'NODE_ID', 'Transaction'),
('Device', 'V_DEVICE', 'NODE_ID', 'Device');

-- ============================================================================================================
-- RELATIONSHIP MAPPINGS (Abstract -> Concrete)
-- setup as relationship_views.SRC_ID,DST_ID and EDGE_TYPE (this comes from Physicallayer.KG_EDGE.EDGE_TYPE)
-- ============================================================================================================
INSERT INTO ONT_REL_MAP (REL_NAME, CONCRETE_VIEW, SRC_COL, DST_COL, PROPS_COL, VIA_REL_VALUE) VALUES
('CUST_OWNS_PRODUCT', 'V_CUST_PRODUCT_OWNED', 'ACCOUNT_ID', 'CUSTOMER_ID', 'PROPS', 'CUST_OWNS_PRODUCT'),
('PRODUCT_TRANSACTIONS', 'V_PRODUCT_TXN_DONE', 'TXN_ID', 'ACCOUNT_ID', 'PROPS', 'PRODUCT_TRANSACTIONS'),
('CUSTOMER_TRANSACTIONS', 'V_CUST_TXN_DONE', 'TXN_ID', 'CUSTOMER_ID', 'PROPS', 'CUSTOMER_TRANSACTIONS'),
('CUSTOMER_DEVICE', 'V_CUST_DEVICE_OWNED', 'DEVICE_ID', 'CUSTOMER_ID', 'PROPS', 'CUSTOMER_DEVICE');
-- Abstract relationships ('<NOTHING ABSTRACT NOW>')

-- =============================================================================
-- INTERFACES
-- setup via seedmetadata.ONT_SHARED_PROPERTY + EntityViews & RelationshipViews
-- =============================================================================
INSERT INTO ONT_INTERFACE (INTERFACE_NAME, DESCRIPTION) VALUES
('Named', 'Entities that have a name property'),
('Temporal', 'Entities with temporal validity'),
('Locatable', 'Entities with information');

INSERT INTO ONT_INTERFACE_PROPERTY (INTERFACE_NAME, PROP_NAME, SHARED_PROP_NAME) VALUES
('Named', 'name', 'name'),
('Temporal', 'opendate', 'entityrelationdt_start'),
('Temporal', 'closeddate', 'entityrelationdt_end'),
('Locatable', 'txn_specific_features', 'transaction');

INSERT INTO ONT_INTERFACE_IMPL (INTERFACE_NAME, CLASS_NAME) VALUES
('Named', 'Customer'),
('Named', 'Account'),
('Named', 'Transaction'),
('Named', 'Device'),
('Temporal', 'Transaction'),
('Locatable', 'Product Transaction'),
('Locatable', 'Customer Transaction');

-- =====================================================
-- INFERENCE RULES
-- setup via seedmetadata.RELATIONSHIP DEFINITIONS
-- =====================================================
INSERT INTO ONT_RULE (RULE_ID, RULE_KIND, TARGET_REL, SOURCE_REL_1, SOURCE_REL_2, INVERSE_OF, IS_ENABLED, DESCRIPTION) VALUES
('RULE_INV_001', 'INVERSE', 'ACC_HAS_CUST', NULL, NULL, 'CUST_OWNS_PRODUCT', TRUE, 'Infer CUST_OWNS_PRODUCT from ACC_HAS_CUST'),
('RULE_INV_002', 'INVERSE', 'ACC_HAS_TXN', NULL, NULL, 'PRODUCT_TRANSACTIONS', TRUE, 'Infer PRODUCT_TRANSACTIONS from ACC_HAS_TXN')
('RULE_INV_003', 'INVERSE', 'CUST_HAS_TXN', NULL, NULL, 'CUST_OWNS_PRODUCT', TRUE, 'Infer CUST_OWNS_PRODUCT from CUST_HAS_TXN'),
('RULE_INV_004', 'INVERSE', 'DEVICE_CUST_OWNS', NULL, NULL, 'CUSTOMER_DEVICE', TRUE, 'Infer CUSTOMER_DEVICE from DEVICE_CUST_OWNS');
-- RULES FOR Abstract relationships ('<NOTHING ABSTRACT NOW>')

-- =====================================================
-- ACTION TYPES
-- =====================================================
INSERT INTO ACT_TYPE (ACTION_TYPE_ID, ACTION_NAME, DESCRIPTION, ONTOLOGY_NAME, TARGET_CLASS, HANDLER_PROC, IS_ENABLED) VALUES
<NOT CONSIDERED NOW - THIS CAN BE USED FOR MULTI HOP TRANSACTIONS - CORRESPONDENT BANKING TYPE>

INSERT INTO ACT_DEF (ACTION_TYPE_ID, PARAM_NAME, PARAM_TYPE, IS_REQUIRED, DESCRIPTION) VALUES
<NOT CONSIDERED NOW - THIS CAN BE USED FOR ENTITIES INVOLVED IN TXN>

-- =====================================================
-- FUNCTIONS
-- =====================================================
INSERT INTO ONT_FUNCTION (ONTOLOGY_NAME, FUNCTION_NAME, VERSION, LANGUAGE, SNOWFLAKE_REF, DESCRIPTION, INPUT_SCHEMA, OUTPUT_SCHEMA)
SELECT 'DATA_V1', 'calculate_age', '1.0', 'SQL', 'FN_CALCULATE_AGE', 'Calculate age from birthdate', 
 PARSE_JSON('{"birthdate": "DATE"}'), 
 PARSE_JSON('{"age": "INTEGER"}')
/**
UNION ALL
SELECT 'DATA_V1', 'graph_shortest_path', '1.0', 'PYTHON', 'SP_GRAPH_SHORTEST_PATH', 'Find shortest path between two nodes',
 PARSE_JSON('{"source_id": "STRING", "target_id": "STRING", "rel_types": "ARRAY"}'),
 PARSE_JSON('{"path": "ARRAY", "length": "INTEGER"}')
**/
UNION ALL
SELECT 'DATA_V1', 'graph_centrality', '1.0', 'PYTHON', 'SP_GRAPH_CENTRALITY', 'Calculate centrality metrics for nodes',
 PARSE_JSON('{"centrality_type": "STRING", "node_type": "STRING"}'),
 PARSE_JSON('{"results": "ARRAY"}');

INSERT INTO ONT_FUNCTION_BINDING (ONTOLOGY_NAME, FUNCTION_NAME, VERSION, BOUND_TO_KIND, BOUND_TO_NAME) VALUES
('DATA_V1', 'calculate_age', '1.0', 'OBJECT_TYPE', 'Customer'),
--('DATA_V1', 'graph_shortest_path', '1.0', 'LINK_TYPE', '<NOT CONSIDERED NOW, CAN BE USED FOR CORRESPONDENT BANKING TYPE TXN TO LINK ACCOUNT / CUSTOMER>'),
('DATA_V1', 'graph_centrality', '1.0', 'OBJECT_TYPE', 'Customer');

-- =====================================================
-- ROLES AND PERMISSIONS
-- =====================================================
INSERT INTO ONT_ROLE (ONTOLOGY_NAME, ONT_ROLE_NAME, DESCRIPTION) VALUES
('DATA_V1', 'viewer', 'Read-only access to all entities'),
('DATA_V1', 'analyst', 'Read access plus analytics functions'),
('DATA_V1', 'editor', 'Read and write access to entities'),
('DATA_V1', 'admin', 'Full administrative access');

INSERT INTO ONT_PERMISSION (ONTOLOGY_NAME, SUBJECT_KIND, SUBJECT_NAME, ONT_ROLE_NAME, PRIVILEGE) VALUES
-- Viewer permissions
('DATA_V1', 'OBJECT_TYPE', 'Customer', 'viewer', 'READ'),
('DATA_V1', 'OBJECT_TYPE', 'Account', 'viewer', 'READ'),
('DATA_V1', 'OBJECT_TYPE', 'Device', 'viewer', 'READ'),
('DATA_V1', 'OBJECT_TYPE', 'Transaction', 'viewer', 'READ'),
--('DATA_V1', 'LINK_TYPE', '<ABSTRACTION RELATIONSHIP CAN BE ADDED HERE>', 'viewer', 'READ'),

-- Analyst permissions (inherits viewer)
('DATA_V1', 'OBJECT_TYPE', 'Customer', 'analyst', 'READ'),
('DATA_V1', 'OBJECT_TYPE', 'Account', 'analyst', 'READ'),
('DATA_V1', 'OBJECT_TYPE', 'Device', 'analyst', 'READ'),
('DATA_V1', 'OBJECT_TYPE', 'Transaction', 'analyst', 'READ'),
--('DATA_V1', 'ACTION_TYPE', 'graph_shortest_path', 'analyst', 'EXECUTE'),
('DATA_V1', 'ACTION_TYPE', 'graph_centrality', 'analyst', 'EXECUTE'),

-- Editor permissions
('DATA_V1', 'OBJECT_TYPE', 'Customer', 'editor', 'WRITE'),
('DATA_V1', 'OBJECT_TYPE', 'Account', 'editor', 'WRITE'),
('DATA_V1', 'OBJECT_TYPE', 'Device', 'editor', 'WRITE'),
('DATA_V1', 'OBJECT_TYPE', 'Transaction', 'editor', 'WRITE'),
--(ACTUAL SEEDMETADATA.ACTION TYPES - ACT_TYPE AND ACT_DEF ENTRIES GO HERE)

-- Admin permissions
('DATA_V1', 'OBJECT_TYPE', 'Customer', 'admin', 'ADMIN'),
('DATA_V1', 'OBJECT_TYPE', 'Account', 'admin', 'ADMIN'),
('DATA_V1', 'OBJECT_TYPE', 'Device', 'admin', 'ADMIN'),
('DATA_V1', 'OBJECT_TYPE', 'Transaction', 'admin', 'ADMIN');

-- =====================================================
-- OBJECT VIEW DEFINITIONS (for governance)
-- =====================================================
INSERT INTO OBJ_VIEW_DEF (OBJ_TYPE, VIEW_NAME, CREATED_BY, DESCRIPTION, DISPLAY_COLS)
SELECT 'Customer', 'V_CUSTOMER', 'SYSTEM', 'Standard customer view', ARRAY_CONSTRUCT('NAME', 'NATIONALITY', 'NATIONALITY')
UNION ALL
SELECT 'Account', 'V_ACCOUNT', 'SYSTEM', 'Standard account view', ARRAY_CONSTRUCT('NAME', 'CUSTOMER_CIS', 'CUSTOMER_CIS')
UNION ALL
SELECT 'Device', 'V_DEVICE', 'SYSTEM', 'Standard device view', ARRAY_CONSTRUCT('NAME', 'CUSTOMER_CIS', 'CUSTOMER_CIS')
UNION ALL
SELECT 'Transaction', 'V_TRANSACTION', 'SYSTEM', 'Standard transaction view', ARRAY_CONSTRUCT('NAME', 'TXN_DATE', 'TXN_DATE');

-- =====================================================
-- OBJECT SOURCE MAPPINGS
-- =====================================================
INSERT INTO ONT_OBJECT_SOURCE (ONTOLOGY_NAME, OBJ_TYPE, SOURCE_TABLE, FILTER_SQL, MAPPING)
SELECT 'DATA_V1', 'Customer', 'KG_NODE', 'NODE_TYPE = ''PLAYER''', 
 PARSE_JSON('{"NODE_ID": "id", "PROPS:NAME": "name", "PROPS:ADDRESS": "address"}')
UNION ALL
SELECT 'DATA_V1', 'Account', 'KG_NODE', 'NODE_TYPE = ''COACH''',
 PARSE_JSON('{"NODE_ID": "id", "PROPS:NAME": "name", "PROPS:CUSTOMER_CIS": "primarycustomer"}')
UNION ALL
SELECT 'DATA_V1', 'Device', 'KG_NODE', 'NODE_TYPE = ''CLUB''',
 PARSE_JSON('{"NODE_ID": "id", "PROPS:CLUB_NAME": "name", "PROPS:CUSTOMER_CIS": "primarycustomer"}')
UNION ALL
SELECT 'DATA_V1', 'Transaction', 'KG_NODE', 'NODE_TYPE = ''MATCH''',
 PARSE_JSON('{"NODE_ID": "id", "PROPS:MATCH_NAME": "name", "PROPS:TXN_DATE": "txndate"}');

-- =====================================================
-- LINK SOURCE MAPPINGS
--CUST_OWNS_PRODUCT | PRODUCT_TRANSACTIONS | CUSTOMER_TRANSACTIONS | CUSTOMER_DEVICE
-- =====================================================
INSERT INTO ONT_LINK_SOURCE (ONTOLOGY_NAME, LINK_TYPE, SOURCE_TABLE, FILTER_SQL, MAPPING)
SELECT 'DATA_V1', 'CUST_OWNS_PRODUCT', 'KG_EDGE', 'EDGE_TYPE = ''CUST_OWNS_PRODUCT''',
 PARSE_JSON('{"SRC_ID": "ACCOUNT_ID", "DST_ID": "CUSTOMER_ID", "EFFECTIVE_START": "entityrelationdt_start"}')
UNION ALL
SELECT 'DATA_V1', 'PRODUCT_TRANSACTIONS', 'KG_EDGE', 'EDGE_TYPE = ''PRODUCT_TRANSACTIONS''',
 PARSE_JSON('{"SRC_ID": "TXN_ID", "DST_ID": "ACCOUNT_ID", "TXN_DATE": "txndate"}')
UNION ALL
SELECT 'DATA_V1', 'CUSTOMER_TRANSACTIONS', 'KG_EDGE', 'EDGE_TYPE = ''CUSTOMER_TRANSACTIONS''',
 PARSE_JSON('{"SRC_ID": "TXN_ID", "DST_ID": "CUSTOMER_ID", "TXN_DATE": "txndate"}');
UNION ALL
SELECT 'DATA_V1', 'CUSTOMER_DEVICE', 'KG_EDGE', 'EDGE_TYPE = ''CUSTOMER_DEVICE''',
 PARSE_JSON('{"SRC_ID": "DEVICE_ID", "DST_ID": "CUSTOMER_ID", "DATE_REGISTERED": "registereddate"}');

COMMIT;