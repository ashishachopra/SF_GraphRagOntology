-- =====================================================
-- LAYER 3: RELATIONSHIP VIEWS (Convenience Views)
-- Type-specific views over KG_EDGE for easier querying
-- =====================================================

USE DATABASE ONTOLOGY_DB;
USE SCHEMA DATA_KG;

-- =======================================================
-- V_CUST_PRODUCT_OWNED: Customer to Account Relationship
-- =======================================================
CREATE OR REPLACE VIEW V_CUST_PRODUCT_OWNED AS
SELECT
    SRC_ID                AS ACCOUNT_ID,
    DST_ID                AS CUSTOMER_ID,
    EDGE_TYPE,
    PROPS,
    WEIGHT,
    EFFECTIVE_START,
    EFFECTIVE_END,
    PROPS:product_type::STRING      		AS PRODUCT_TYPE, --This is the KG_EDGE.PROPS <product_type, product_specific_attributes>
    PROPS:product_specific_attributes::STRING 	AS PRODUCT_FEATURES 
FROM KG_EDGE
WHERE EDGE_TYPE = 'CUST_OWNS_PRODUCT'; --This is the KG_EDGE.EDGE_TYPE <CUST_OWNS_PRODUCT | PRODUCT_TRANSACTIONS | CUSTOMER_TRANSACTIONS | CUSTOMER_DEVICE>

COMMENT ON VIEW V_CUST_PRODUCT_OWNED IS 'Customer to Account Relationship';

-- =====================================================
-- V_CUST_DEVICE_OWNED: Customer to Device Relationships
-- =====================================================
CREATE OR REPLACE VIEW V_CUST_DEVICE_OWNED AS
SELECT
    SRC_ID                AS DEVICE_ID,
    DST_ID                AS CUSTOMER_ID,
    EDGE_TYPE,
    PROPS,
    WEIGHT,
    EFFECTIVE_START,
    EFFECTIVE_END,
    PROPS:device_type::STRING     		AS DEVICE_TYPE, --This is the KG_EDGE.PROPS <device_type, device_specific_features>
    PROPS:device_specific_features::STRING    	AS DEVICE_FEATURES,
    PROPS:imei::STRING   		        AS IMEI,
    PROPS:version::STRING    			AS PHONE_VERSION,
    PROPS:registereddate::DATE       		AS DATE_REGISTERED
FROM KG_EDGE
WHERE EDGE_TYPE = 'CUSTOMER_DEVICE'; --This is the KG_EDGE.EDGE_TYPE <CUSTOMER_DEVICE>

COMMENT ON VIEW V_CUST_DEVICE_OWNED IS 'Customer to Device Relationships';

-- =======================================================
-- V_CUST_TXN_DONE: Customer to Transaction Relationships
-- =======================================================
CREATE OR REPLACE VIEW V_CUST_TXN_DONE AS
SELECT
    SRC_ID                AS TXN_ID,
    DST_ID                AS CUSTOMER_ID,
    EDGE_TYPE,
    PROPS,
    WEIGHT,
    EFFECTIVE_START,
    EFFECTIVE_END,
    PROPS:txn_type::STRING     			AS TXN_TYPE, --This is the KG_EDGE.PROPS <transaction_type, transaction_specific_attributes - customer grain>
    PROPS:txn_specific_features::STRING    	AS TXN_FEATURES
FROM KG_EDGE
WHERE EDGE_TYPE = 'CUSTOMER_TRANSACTIONS';

COMMENT ON VIEW V_CUST_TXN_DONE IS 'Customer to Transaction Relationships';

-- ==========================================================
-- V_PRODUCT_TXN_DONE: Product to Transaction Relationships
-- ==========================================================
CREATE OR REPLACE VIEW V_PRODUCT_TXN_DONE AS
SELECT
    SRC_ID                AS TXN_ID,
    DST_ID                AS ACCOUNT_ID,
    EDGE_TYPE,
    PROPS,
    WEIGHT,
    EFFECTIVE_START,
    EFFECTIVE_END,
    PROPS:txn_type::STRING     			AS TXN_TYPE, --This is the KG_EDGE.PROPS <transaction_type, transaction_specific_attributes - product grain>
    PROPS:txn_specific_features::STRING    	AS TXN_FEATURES
FROM KG_EDGE
WHERE EDGE_TYPE = 'PRODUCT_TRANSACTIONS';

COMMENT ON VIEW V_PRODUCT_TXN_DONE IS 'Product to Transaction Relationships';
-- =========================================================================================================================
-- NOTE: ACTIVE_RELATIONSHIPS and MATCH_RESULTS views would be defined in abstract_views.sql with richer schemas
-- =========================================================================================================================