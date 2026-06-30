-- =====================================================
-- LAYER 3: ENTITY VIEWS (Convenience Views)
-- Type-specific views over KG_NODE for easier querying
-- =====================================================

USE DATABASE ONTOLOGY_DB;
USE SCHEMA DATA_KG;

-- =====================================================
-- V_CUSTOMER: View of all customers
-- =====================================================
CREATE OR REPLACE VIEW V_CUSTOMER AS
SELECT
    NODE_ID,
    NAME,
    PROPS:customertype::STRING  AS CUSTOMERTYPE,
    PROPS:nationality::STRING   AS NATIONALITY,
    PROPS:birthdate::DATE       AS BIRTHDATE,
    PROPS:email::STRING      	AS EMAIL,
    PROPS:phonenumber::STRING  	AS PHONE,
    PROPS:address::STRING       AS ADDRESS,
    PROPS
FROM KG_NODE
WHERE NODE_TYPE = 'CUSTOMER';
COMMENT ON VIEW V_CUSTOMER IS 'Convenience view for Customer entities with extracted properties';

-- =====================================================
-- V_ACCOUNT: View of all accounts
-- =====================================================
CREATE OR REPLACE VIEW V_ACCOUNT AS
SELECT
    NODE_ID,
    NAME,
    PROPS:accounttype::STRING     	AS ACCOUNTTYPE,
    PROPS:primarycustomer::STRING       AS CUSTOMER_CIS,
    PROPS:opendate::DATE          	AS OPENDATE,
    PROPS:closeddate::DATE        	AS CLOSEDDATE,
    PROPS:accountbalance::INTEGER 	AS ACCOUNT_BAL,
    PROPS:relationshipmanager::STRING 	AS REL_MANAGER,
    PROPS
FROM KG_NODE
WHERE NODE_TYPE = 'ACCOUNT';
COMMENT ON VIEW V_ACCOUNT IS 'Convenience view for Account entities with extracted properties';

-- =====================================================
-- V_TRANSACTION: View of all transactions
-- =====================================================
CREATE OR REPLACE VIEW V_TRANSACTION AS
SELECT
    NODE_ID,
    NAME,
    PROPS:txndate::DATE      		AS TXN_DATE,
    PROPS:amount::INTEGER         	AS AMOUNT,
    PROPS:basecurrency::STRING   	AS BASE_CURRENCY,
    PROPS:actualcurrency::STRING       	AS ACTUAL_CURRENCY,
    PROPS:creditdebit::INTEGER   	AS CREDIT_DEBIT_CODE,
    PROPS:primarycustomer::STRING       AS CUSTOMER_CIS,
    PROPS:account::STRING       	AS ACCOUNT_KEY,
    PROPS:device::STRING       		AS DEVICE_ID,
    PROPS
FROM KG_NODE
WHERE NODE_TYPE = 'TRANSACTION';
COMMENT ON VIEW V_TRANSACTION IS 'Convenience view for Device entities with extracted properties';

-- =====================================================
-- V_DEVICE: View of all devices
-- =====================================================
CREATE OR REPLACE VIEW V_DEVICE AS
SELECT
    NODE_ID,
    NAME,
    PROPS:registereddate::DATE      	AS REGISTERED_DATE,
    PROPS:devicetype::STRING         	AS DEVICE_TYPE,
    PROPS:imeinumber::STRING   		AS IMEI,
    PROPS:primarycustomer::STRING       AS CUSTOMER_CIS,
    PROPS:version::INTEGER   		AS VERSION,
    PROPS:phonenumber::STRING  	 	AS PHONE,
    PROPS
FROM KG_NODE
WHERE NODE_TYPE = 'DEVICE';
COMMENT ON VIEW V_DEVICE IS 'Convenience view for Device entities with extracted properties';