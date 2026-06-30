-- =====================================================
-- LAYER 3: ABSTRACT VIEWS
-- Pre-built abstract views for the ontology layer
-- =====================================================

USE DATABASE ONTOLOGY_DB;
USE SCHEMA DATA_KG;

-- =====================================================
-- VW_ONT_CUSTOMER - Abstract Customer View
-- Unifies all person types (customer, counterparty)
-- =====================================================
CREATE OR REPLACE VIEW VW_ONT_CUSTOMER AS
SELECT 
    NODE_ID AS ID,
    'Customer' AS SUBTYPE,
    'V_CUSTOMER' AS SRC_VIEW
FROM V_CUSTOMER;

/**UNION ALL

SELECT 
    NODE_ID AS ID,
    'CounterParty' AS SUBTYPE,
    'V_COUNTERPARTY' AS SRC_VIEW
FROM V_COUNTERPARTY;**/

COMMENT ON VIEW VW_ONT_CUSTOMER IS 'Abstract view unifying all customer types (customer, counterparty)';

-- =========================================================
-- VW_ONT_PRODUCT - Abstract Product View
-- Unifies all Product types (All Products - Cross Divison)
-- =========================================================
CREATE OR REPLACE VIEW VW_ONT_ACCOUNT AS
SELECT 
    NODE_ID AS ID,
    'Product' AS SUBTYPE,
    'V_ACCOUNT' AS SRC_VIEW
FROM V_ACCOUNT;

COMMENT ON VIEW VW_ONT_ACCOUNT IS 'Abstract view unifying all PRODUCT types (All Products - Cross Divison)';

-- ==========================================================================
-- VW_ONT_EVENT - Abstract Event View
-- Unifies all event types (Matches - CustAcc, AccTxn, CustTxn, CustDevice)
-- ==========================================================================
/**CREATE OR REPLACE VIEW VW_ONT_EVENT AS
SELECT 
    NODE_ID AS ID,
    'Match' AS SUBTYPE,
    'V_MATCH' AS SRC_VIEW
FROM V_MATCH;

COMMENT ON VIEW VW_ONT_EVENT IS 'Abstract view unifying all event types (CustAcc, AccTxn, CustTxn, CustDevice)';**/

-- =====================================================
-- REL_RESOLVED - Unified Relationship View
-- Combines all concrete relationships with type resolution
-- <THIS IS RELATIONSHIP_VIEW.V_CUST_PRODUCT_OWNED.PROPS> 
-- CUST_OWNS_PRODUCT | PRODUCT_TRANSACTIONS | CUSTOMER_TRANSACTIONS | CUSTOMER_DEVICE
-- =====================================================
CREATE OR REPLACE VIEW REL_RESOLVED AS
-- CUST_PRODUCT_OWNED relationships (Customer -> Product)
SELECT
    'CUST_OWNS_PRODUCT' AS REL_NAME,
    ACCOUNT_ID AS SRC_ID,
    'Account' AS SRC_CLASS,
    CUSTOMER_ID AS DST_ID,
    'Customer' AS DST_CLASS,
    EFFECTIVE_START,
    EFFECTIVE_END,
    OBJECT_CONSTRUCT(
        'PRODUCT_TYPE', PRODUCT_TYPE,
        'PRODUCT_FEATURES', PRODUCT_FEATURES
    ) AS PROPS,
    1.0 AS WEIGHT
FROM V_CUST_PRODUCT_OWNED

UNION ALL

-- CUSTOMER_DEVICE relationships (Customer -> Device)
SELECT
    'CUSTOMER_DEVICE' AS REL_NAME,
    DEVICE_ID AS SRC_ID,
    'Device' AS SRC_CLASS,
    Customer_ID AS DST_ID,
    'Customer' AS DST_CLASS,
    EFFECTIVE_START,
    EFFECTIVE_END,
    OBJECT_CONSTRUCT(
	'DEVICE_TYPE', DEVICE_TYPE,
	'DEVICE_FEATURES', DEVICE_FEATURES,
    	'IMEI', IMEI,
        'PHONE_VERSION', PHONE_VERSION,
	'DATE_REGISTERED', DATE_REGISTERED
    ) AS PROPS,
    1.0 AS WEIGHT
FROM V_CUST_DEVICE_OWNED

UNION ALL

-- CUSTOMER_TRANSACTIONS relationships (Customer -> Transaction)
SELECT
    'CUSTOMER_TRANSACTIONS ' AS REL_NAME,
    TXN_ID AS SRC_ID,
    'Transaction' AS SRC_CLASS,
    Customer_ID AS DST_ID,
    'Customer' AS DST_CLASS,
    EFFECTIVE_START,
    EFFECTIVE_END,
    OBJECT_CONSTRUCT(
	'TXN_TYPE', TXN_TYPE,
	'TXN_FEATURES', TXN_FEATURES --customer grain
    ) AS PROPS,
    1.0 AS WEIGHT
FROM V_CUST_TXN_DONE

UNION ALL

-- PRODUCT_TRANSACTIONS relationships (Account -> Transaction)
SELECT
    'PRODUCT_TRANSACTIONS' AS REL_NAME,
    TXN_ID AS SRC_ID,
    'Transaction' AS SRC_CLASS,
    Account_ID AS DST_ID,
    'Account' AS DST_CLASS,
    EFFECTIVE_START,
    EFFECTIVE_END,
    OBJECT_CONSTRUCT(
	'TXN_TYPE', TXN_TYPE,
	'TXN_FEATURES', TXN_FEATURES --product grain
    ) AS
    PROPS,
    1.0 AS WEIGHT
FROM V_PRODUCT_TXN_DONE;

COMMENT ON VIEW REL_RESOLVED IS 'Unified view of all relationships with resolved type information';

-- ====================================================================
-- VW_ONT_TXN_FOR - Abstract "Txn for" relationship
-- Unifies PRODUCT_TRANSACTIONS | CUSTOMER_TRANSACTIONS relationships
-- ====================================================================
CREATE OR REPLACE VIEW VW_ONT_TXN_FOR AS
SELECT
    'PRODUCT_TRANSACTIONS' AS VIA_REL,
    SRC_ID AS SUBJECT_ID,
    'Transaction' AS SUBJECT_CLASS,
    DST_ID AS OBJECT_ID,
    'Account' AS OBJECT_CLASS,
    EFFECTIVE_START,
    EFFECTIVE_END,
    PROPS,
    WEIGHT
FROM REL_RESOLVED
WHERE REL_NAME = 'PRODUCT_TRANSACTIONS'

UNION ALL

SELECT
    'CUSTOMER_TRANSACTIONS ' AS VIA_REL,
    SRC_ID AS SUBJECT_ID,
    'Transaction' AS SUBJECT_CLASS,
    DST_ID AS OBJECT_ID,
    'Customer' AS OBJECT_CLASS,
    EFFECTIVE_START,
    EFFECTIVE_END,
    PROPS,
    WEIGHT
FROM REL_RESOLVED
WHERE REL_NAME = 'CUSTOMER_TRANSACTIONS';

COMMENT ON VIEW VW_ONT_TXN_FOR IS 'Abstract relationship unifying PRODUCT_TRANSACTIONS | CUSTOMER_TRANSACTIONS relationships (Account / Customer -> Transaction )';

-- =========================================================================
-- VW_ONT_CUSTOMER_DEVICE_USE - Abstract "Customer Device in" relationship
-- Unifies CUSTOMER_DEVICE relationships
-- =========================================================================
CREATE OR REPLACE VIEW VW_ONT_PARTICIPATES_IN AS
SELECT
    'CUSTOMER_DEVICE' AS VIA_REL,
    SRC_ID AS SUBJECT_ID,
    'Device' AS SUBJECT_CLASS,
    DST_ID AS OBJECT_ID,
    'Customer' AS OBJECT_CLASS,
    EFFECTIVE_START,
    EFFECTIVE_END,
    PROPS,
    WEIGHT
FROM REL_RESOLVED
WHERE REL_NAME = 'CUSTOMER_DEVICE';

COMMENT ON VIEW VW_ONT_PARTICIPATES_IN IS 'Abstract relationship for participation (Customer -> Device)';

-- =================================================================
-- VW_ONT_CUST_PRODUCT_LNK - Abstract "affiliated with" relationship
-- Unifies CUST_PRODUCT_OWNED relationships
-- =================================================================
CREATE OR REPLACE VIEW VW_ONT_CUST_PRODUCT_LNK AS
SELECT
    'CUST_PRODUCT_OWNED' AS VIA_REL,
    SRC_ID AS SUBJECT_ID,
    'Account' AS SUBJECT_CLASS,
    DST_ID AS OBJECT_ID,
    'Customer' AS OBJECT_CLASS,
    EFFECTIVE_START,
    EFFECTIVE_END,
    PROPS,
    WEIGHT
FROM REL_RESOLVED
WHERE REL_NAME = 'CUST_PRODUCT_OWNED';

COMMENT ON VIEW VW_ONT_CUST_PRODUCT_LNK IS 'Abstract relationship for affiliation (Account -> Customer)';

-- =====================================================
-- ONT_CLASS_CLOSURE - Recursive closure of class hierarchy
-- For finding all subtypes of an abstract class
-- =====================================================
CREATE OR REPLACE VIEW ONT_CLASS_CLOSURE AS
WITH RECURSIVE class_tree(ancestor, descendant, depth) AS (
    -- Base case: each class is its own ancestor at depth 0
    SELECT CLASS_NAME, CLASS_NAME, 0
    FROM ONT_CLASS
    
    UNION ALL
    
    -- Recursive case: follow parent relationships
    SELECT ct.ancestor, c.CLASS_NAME, ct.depth + 1
    FROM class_tree ct
    JOIN ONT_CLASS c ON c.PARENT_CLASS_NAME = ct.descendant
    WHERE ct.depth < 10
)
SELECT DISTINCT ancestor AS ANCESTOR_CLASS, descendant AS DESCENDANT_CLASS, depth AS DEPTH
FROM class_tree
ORDER BY ancestor, depth, descendant;

COMMENT ON VIEW ONT_CLASS_CLOSURE IS 'Transitive closure of class hierarchy for polymorphic queries';

-- =====================================================
-- ACTIVE_RELATIONSHIPS - Players with current contracts
-- =====================================================
CREATE OR REPLACE VIEW ACTIVE_RELATIONSHIPS AS
SELECT 
    p.NODE_ID,
    p.NAME AS CUSTOMER_NAME,
    p.PHONE,
    p.NATIONALITY,
    p.BIRTHDATE,
    c.NAME AS ACCOUNT_NAME,
    d.NAME AS DEVICE_NAME
    -- fetch pf.PROP values
    -- fetch df.PROP values
FROM V_CUSTOMER p
LEFT OUTER JOIN V_CUST_PRODUCT_OWNED pf ON p.NODE_ID = pf.CUSTOMER_ID
LEFT OUTER JOIN V_CUST_DEVICE_OWNED df ON p.NODE_ID = df.CUSTOMER_ID
LEFT OUTER JOIN V_ACCOUNT c ON p.NODE_ID = c.customer_cis
LEFT OUTER JOIN V_DEVICE d ON p.NODE_ID = d.CUSTOMER_CIS
WHERE pf.EFFECTIVE_END IS NULL 
   OR pf.EFFECTIVE_END >= CURRENT_DATE();

COMMENT ON VIEW ACTIVE_RELATIONSHIPS IS 'Customers with currently active products and devices';