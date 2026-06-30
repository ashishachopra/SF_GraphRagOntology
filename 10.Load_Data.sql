-- Insert dummy data for Customer, Account, Transaction, Device entities into KG_NODE and KG_EDGE tables
-- ============================================
-- INSERT NODES (Customers, Accounts, Transactions, Devices)
-- ============================================

-- Insert Customers
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_NODE 
    (NODE_ID, NODE_TYPE, NAME, PROPS, TS_INGESTED)
SELECT column1, column2, column3, 
       OBJECT_CONSTRUCT('email', column4, 'phone', column5, 'risk_score', column6, 'kyc_status', column7, 'registration_date', column8), 
       CURRENT_TIMESTAMP()
FROM VALUES
    ('CUST001', 'Customer', 'John Smith', 'john.smith@email.com', '+1-555-0101', 25, 'verified', TO_DATE('2023-01-15')),
    ('CUST002', 'Customer', 'Sarah Johnson', 'sarah.j@email.com', '+1-555-0102', 15, 'verified', TO_DATE('2023-03-22')),
    ('CUST003', 'Customer', 'Michael Chen', 'mchen@email.com', '+1-555-0103', 45, 'pending', TO_DATE('2024-11-05')),
    ('CUST004', 'Customer', 'Emily Rodriguez', 'emily.r@email.com', '+1-555-0104', 10, 'verified', TO_DATE('2022-08-30')),
    ('CUST005', 'Customer', 'David Williams', 'dwilliams@email.com', '+1-555-0105', 78, 'flagged', TO_DATE('2024-12-20'));

-- Insert Accounts
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_NODE 
    (NODE_ID, NODE_TYPE, NAME, PROPS, TS_INGESTED)
SELECT column1, column2, column3,
       OBJECT_CONSTRUCT('account_number', column4, 'account_type', column5, 'balance', column6, 'currency', column7, 'status', column8, 'opened_date', column9),
       CURRENT_TIMESTAMP()
FROM VALUES
    ('ACCT001', 'Account', 'Checking Account - 1001', '1001', 'checking', 15000.00, 'USD', 'active', TO_DATE('2023-01-20')),
    ('ACCT002', 'Account', 'Savings Account - 1002', '1002', 'savings', 45000.00, 'USD', 'active', TO_DATE('2023-03-25')),
    ('ACCT003', 'Account', 'Checking Account - 1003', '1003', 'checking', 2500.00, 'USD', 'active', TO_DATE('2024-11-10')),
    ('ACCT004', 'Account', 'Business Account - 1004', '1004', 'business', 125000.00, 'USD', 'active', TO_DATE('2022-09-05')),
    ('ACCT005', 'Account', 'Checking Account - 1005', '1005', 'checking', 8500.00, 'USD', 'frozen', TO_DATE('2024-12-25')),
    ('ACCT006', 'Account', 'Savings Account - 1006', '1006', 'savings', 22000.00, 'USD', 'active', TO_DATE('2023-01-25'));

-- Insert Transactions
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_NODE 
    (NODE_ID, NODE_TYPE, NAME, PROPS, TS_INGESTED)
SELECT column1, column2, column3,
       OBJECT_CONSTRUCT('amount', column4, 'currency', column5, 'transaction_type', column6, 'status', column7, 'transaction_date', column8, 'channel', column9),
       CURRENT_TIMESTAMP()
FROM VALUES
    ('TXN001', 'Transaction', 'Transfer TXN001', 500.00, 'USD', 'transfer', 'completed', TO_DATE('2026-06-15'), 'online'),
    ('TXN002', 'Transaction', 'Withdrawal TXN002', 200.00, 'USD', 'withdrawal', 'completed', TO_DATE('2026-06-18'), 'atm'),
    ('TXN003', 'Transaction', 'Deposit TXN003', 5000.00, 'USD', 'deposit', 'completed', TO_DATE('2026-06-20'), 'branch'),
    ('TXN004', 'Transaction', 'Transfer TXN004', 15000.00, 'USD', 'transfer', 'flagged', TO_DATE('2026-06-22'), 'online'),
    ('TXN005', 'Transaction', 'Payment TXN005', 350.00, 'USD', 'payment', 'completed', TO_DATE('2026-06-25'), 'mobile'),
    ('TXN006', 'Transaction', 'Transfer TXN006', 1000.00, 'USD', 'transfer', 'completed', TO_DATE('2026-06-26'), 'online'),
    ('TXN007', 'Transaction', 'Withdrawal TXN007', 9500.00, 'USD', 'withdrawal', 'blocked', TO_DATE('2026-06-28'), 'online');

-- Insert Devices
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_NODE 
    (NODE_ID, NODE_TYPE, NAME, PROPS, TS_INGESTED)
SELECT column1, column2, column3,
       OBJECT_CONSTRUCT('device_type', column4, 'os', column5, 'ip_address', column6, 'device_id', column7, 'first_seen', column8, 'last_seen', column9),
       CURRENT_TIMESTAMP()
FROM VALUES
    ('DEV001', 'Device', 'iPhone 14 Pro', 'mobile', 'iOS 17.2', '192.168.1.101', 'ABC123XYZ', TO_DATE('2023-01-15'), TO_DATE('2026-06-28')),
    ('DEV002', 'Device', 'MacBook Pro', 'desktop', 'macOS 14.0', '192.168.1.102', 'DEF456UVW', TO_DATE('2023-03-22'), TO_DATE('2026-06-27')),
    ('DEV003', 'Device', 'Samsung Galaxy S24', 'mobile', 'Android 14', '10.0.0.50', 'GHI789RST', TO_DATE('2024-11-05'), TO_DATE('2026-06-28')),
    ('DEV004', 'Device', 'iPad Air', 'tablet', 'iPadOS 17.1', '192.168.1.103', 'JKL012MNO', TO_DATE('2022-08-30'), TO_DATE('2026-06-20')),
    ('DEV005', 'Device', 'Unknown Device', 'unknown', 'unknown', '45.67.89.12', 'PQR345STU', TO_DATE('2024-12-20'), TO_DATE('2026-06-28'));

-- ============================================
-- INSERT EDGES (Relationships)
-- ============================================

-- Customer -> Account relationships (OWNS)
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_EDGE 
    (EDGE_ID, EDGE_TYPE, SRC_ID, DST_ID, EFFECTIVE_START, EFFECTIVE_END, WEIGHT, PROPS, TS_INGESTED)
SELECT column1, column2, column3, column4, column5, column6, column7,
       OBJECT_CONSTRUCT('relationship', column8, 'ownership_pct', column9),
       CURRENT_TIMESTAMP()
FROM VALUES
    ('EDGE001', 'OWNS', 'CUST001', 'ACCT001', TO_DATE('2023-01-20'), NULL, 1.0, 'primary_owner', 100),
    ('EDGE002', 'OWNS', 'CUST001', 'ACCT006', TO_DATE('2023-01-25'), NULL, 1.0, 'primary_owner', 100),
    ('EDGE003', 'OWNS', 'CUST002', 'ACCT002', TO_DATE('2023-03-25'), NULL, 1.0, 'primary_owner', 100),
    ('EDGE004', 'OWNS', 'CUST003', 'ACCT003', TO_DATE('2024-11-10'), NULL, 1.0, 'primary_owner', 100),
    ('EDGE005', 'OWNS', 'CUST004', 'ACCT004', TO_DATE('2022-09-05'), NULL, 1.0, 'primary_owner', 100),
    ('EDGE006', 'OWNS', 'CUST005', 'ACCT005', TO_DATE('2024-12-25'), NULL, 1.0, 'primary_owner', 100);

-- Transaction -> Account relationships (FROM_ACCOUNT)
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_EDGE 
    (EDGE_ID, EDGE_TYPE, SRC_ID, DST_ID, EFFECTIVE_START, EFFECTIVE_END, WEIGHT, PROPS, TS_INGESTED)
SELECT column1, column2, column3, column4, column5, column6, column7,
       OBJECT_CONSTRUCT('role', column8),
       CURRENT_TIMESTAMP()
FROM VALUES
    ('EDGE007', 'FROM_ACCOUNT', 'TXN001', 'ACCT001', TO_DATE('2026-06-15'), TO_DATE('2026-06-15'), 1.0, 'source'),
    ('EDGE008', 'FROM_ACCOUNT', 'TXN002', 'ACCT001', TO_DATE('2026-06-18'), TO_DATE('2026-06-18'), 1.0, 'source'),
    ('EDGE009', 'FROM_ACCOUNT', 'TXN003', 'ACCT002', TO_DATE('2026-06-20'), TO_DATE('2026-06-20'), 1.0, 'source'),
    ('EDGE010', 'FROM_ACCOUNT', 'TXN004', 'ACCT003', TO_DATE('2026-06-22'), TO_DATE('2026-06-22'), 1.0, 'source'),
    ('EDGE011', 'FROM_ACCOUNT', 'TXN005', 'ACCT004', TO_DATE('2026-06-25'), TO_DATE('2026-06-25'), 1.0, 'source'),
    ('EDGE012', 'FROM_ACCOUNT', 'TXN006', 'ACCT001', TO_DATE('2026-06-26'), TO_DATE('2026-06-26'), 1.0, 'source'),
    ('EDGE013', 'FROM_ACCOUNT', 'TXN007', 'ACCT005', TO_DATE('2026-06-28'), TO_DATE('2026-06-28'), 1.0, 'source');

-- Transaction -> Account relationships (TO_ACCOUNT)
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_EDGE 
    (EDGE_ID, EDGE_TYPE, SRC_ID, DST_ID, EFFECTIVE_START, EFFECTIVE_END, WEIGHT, PROPS, TS_INGESTED)
SELECT column1, column2, column3, column4, column5, column6, column7,
       OBJECT_CONSTRUCT('role', column8),
       CURRENT_TIMESTAMP()
FROM VALUES
    ('EDGE014', 'TO_ACCOUNT', 'TXN001', 'ACCT002', TO_DATE('2026-06-15'), TO_DATE('2026-06-15'), 1.0, 'destination'),
    ('EDGE015', 'TO_ACCOUNT', 'TXN004', 'ACCT004', TO_DATE('2026-06-22'), TO_DATE('2026-06-22'), 1.0, 'destination'),
    ('EDGE016', 'TO_ACCOUNT', 'TXN006', 'ACCT006', TO_DATE('2026-06-26'), TO_DATE('2026-06-26'), 1.0, 'destination');

-- Customer -> Device relationships (USES_DEVICE)
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_EDGE 
    (EDGE_ID, EDGE_TYPE, SRC_ID, DST_ID, EFFECTIVE_START, EFFECTIVE_END, WEIGHT, PROPS, TS_INGESTED)
SELECT column1, column2, column3, column4, column5, column6, column7,
       OBJECT_CONSTRUCT('usage_frequency', column8, 'primary_device', column9),
       CURRENT_TIMESTAMP()
FROM VALUES
    ('EDGE017', 'USES_DEVICE', 'CUST001', 'DEV001', TO_DATE('2023-01-15'), NULL, 1.0, 'daily', TRUE),
    ('EDGE018', 'USES_DEVICE', 'CUST001', 'DEV002', TO_DATE('2023-01-15'), NULL, 0.8, 'weekly', FALSE),
    ('EDGE019', 'USES_DEVICE', 'CUST002', 'DEV002', TO_DATE('2023-03-22'), NULL, 1.0, 'daily', TRUE),
    ('EDGE020', 'USES_DEVICE', 'CUST003', 'DEV003', TO_DATE('2024-11-05'), NULL, 1.0, 'daily', TRUE),
    ('EDGE021', 'USES_DEVICE', 'CUST004', 'DEV004', TO_DATE('2022-08-30'), NULL, 1.0, 'daily', TRUE),
    ('EDGE022', 'USES_DEVICE', 'CUST005', 'DEV005', TO_DATE('2024-12-20'), NULL, 1.0, 'sporadic', TRUE);

-- Transaction -> Device relationships (INITIATED_FROM)
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_EDGE 
    (EDGE_ID, EDGE_TYPE, SRC_ID, DST_ID, EFFECTIVE_START, EFFECTIVE_END, WEIGHT, PROPS, TS_INGESTED)
SELECT column1, column2, column3, column4, column5, column6, column7,
       OBJECT_CONSTRUCT('ip_address', column8, 'location', column9),
       CURRENT_TIMESTAMP()
FROM VALUES
    ('EDGE023', 'INITIATED_FROM', 'TXN001', 'DEV001', TO_DATE('2026-06-15'), TO_DATE('2026-06-15'), 1.0, '192.168.1.101', 'New York, NY'),
    ('EDGE024', 'INITIATED_FROM', 'TXN002', 'DEV001', TO_DATE('2026-06-18'), TO_DATE('2026-06-18'), 1.0, '192.168.1.101', 'New York, NY'),
    ('EDGE025', 'INITIATED_FROM', 'TXN003', 'DEV002', TO_DATE('2026-06-20'), TO_DATE('2026-06-20'), 1.0, '192.168.1.102', 'Boston, MA'),
    ('EDGE026', 'INITIATED_FROM', 'TXN004', 'DEV003', TO_DATE('2026-06-22'), TO_DATE('2026-06-22'), 1.0, '10.0.0.50', 'Unknown'),
    ('EDGE027', 'INITIATED_FROM', 'TXN005', 'DEV004', TO_DATE('2026-06-25'), TO_DATE('2026-06-25'), 1.0, '192.168.1.103', 'Chicago, IL'),
    ('EDGE028', 'INITIATED_FROM', 'TXN006', 'DEV001', TO_DATE('2026-06-26'), TO_DATE('2026-06-26'), 1.0, '192.168.1.101', 'New York, NY'),
    ('EDGE029', 'INITIATED_FROM', 'TXN007', 'DEV005', TO_DATE('2026-06-28'), TO_DATE('2026-06-28'), 1.0, '45.67.89.12', 'Unknown');

-- Customer -> Customer relationships (RELATED_TO) - family/business connections
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_EDGE 
    (EDGE_ID, EDGE_TYPE, SRC_ID, DST_ID, EFFECTIVE_START, EFFECTIVE_END, WEIGHT, PROPS, TS_INGESTED)
SELECT column1, column2, column3, column4, column5, column6, column7,
       OBJECT_CONSTRUCT('relationship_type', column8, 'confidence', column9),
       CURRENT_TIMESTAMP()
FROM VALUES
    ('EDGE030', 'RELATED_TO', 'CUST001', 'CUST002', TO_DATE('2023-01-15'), NULL, 0.7, 'spouse', 0.95),
    ('EDGE031', 'RELATED_TO', 'CUST002', 'CUST001', TO_DATE('2023-01-15'), NULL, 0.7, 'spouse', 0.95),
    ('EDGE032', 'RELATED_TO', 'CUST003', 'CUST005', TO_DATE('2024-11-05'), NULL, 0.3, 'suspicious_link', 0.45);

-- Generate 75K sample records for knowledge graph with customers, accounts, transactions, and devices
-- Step 1: Generate 20,000 Customer nodes
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_NODE (NODE_ID, NODE_TYPE, NAME, PROPS)
SELECT
    'CUST' || LPAD(seq4(), 6, '0') AS NODE_ID,
    'Customer' AS NODE_TYPE,
    CASE (UNIFORM(1, 20, RANDOM()))
        WHEN 1 THEN 'John Smith'
        WHEN 2 THEN 'Sarah Johnson'
        WHEN 3 THEN 'Michael Chen'
        WHEN 4 THEN 'Emily Rodriguez'
        WHEN 5 THEN 'David Williams'
        WHEN 6 THEN 'Lisa Anderson'
        WHEN 7 THEN 'James Martinez'
        WHEN 8 THEN 'Maria Garcia'
        WHEN 9 THEN 'Robert Taylor'
        WHEN 10 THEN 'Jennifer Lee'
        WHEN 11 THEN 'William Brown'
        WHEN 12 THEN 'Jessica Davis'
        WHEN 13 THEN 'Richard Wilson'
        WHEN 14 THEN 'Linda Moore'
        WHEN 15 THEN 'Thomas Jackson'
        WHEN 16 THEN 'Patricia White'
        WHEN 17 THEN 'Christopher Harris'
        WHEN 18 THEN 'Nancy Martin'
        WHEN 19 THEN 'Daniel Thompson'
        ELSE 'Karen Garcia'
    END || ' ' || seq4() AS NAME,
    OBJECT_CONSTRUCT(
        'email', 'user' || seq4() || '@email.com',
        'kyc_status', CASE UNIFORM(1, 100, RANDOM()) 
            WHEN 95 THEN 'flagged'
            WHEN 96 THEN 'pending'
            ELSE 'verified'
        END,
        'phone', '+1-555-' || LPAD(UNIFORM(1000, 9999, RANDOM()), 4, '0'),
        'registration_date', DATEADD(day, -UNIFORM(1, 1460, RANDOM()), CURRENT_DATE())::STRING,
        'risk_score', UNIFORM(1, 100, RANDOM()),
        'country', CASE (UNIFORM(1, 10, RANDOM()))
            WHEN 1 THEN 'USA'
            WHEN 2 THEN 'Canada'
            WHEN 3 THEN 'UK'
            WHEN 4 THEN 'Germany'
            WHEN 5 THEN 'France'
            WHEN 6 THEN 'Australia'
            WHEN 7 THEN 'Japan'
            WHEN 8 THEN 'Singapore'
            ELSE 'USA'
        END,
        'customer_tier', CASE (UNIFORM(1, 10, RANDOM()))
            WHEN 1 THEN 'platinum'
            WHEN 2 THEN 'gold'
            WHEN 3 THEN 'silver'
            ELSE 'standard'
        END
    ) AS PROPS
FROM TABLE(GENERATOR(ROWCOUNT => 20000));

-- Step 2: Generate 25,000 Account nodes
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_NODE (NODE_ID, NODE_TYPE, NAME, PROPS)
SELECT
    'ACCT' || LPAD(seq4(), 6, '0') AS NODE_ID,
    'Account' AS NODE_TYPE,
    CASE (UNIFORM(1, 5, RANDOM()))
        WHEN 1 THEN 'Checking Account'
        WHEN 2 THEN 'Savings Account'
        WHEN 3 THEN 'Business Account'
        WHEN 4 THEN 'Investment Account'
        ELSE 'Credit Account'
    END || ' #' || seq4() AS NAME,
    OBJECT_CONSTRUCT(
        'account_number', 'ACC-' || LPAD(seq4(), 10, '0'),
        'account_type', CASE (UNIFORM(1, 5, RANDOM()))
            WHEN 1 THEN 'checking'
            WHEN 2 THEN 'savings'
            WHEN 3 THEN 'business'
            WHEN 4 THEN 'investment'
            ELSE 'credit'
        END,
        'balance', ROUND(UNIFORM(100, 500000, RANDOM()), 2),
        'currency', CASE (UNIFORM(1, 5, RANDOM()))
            WHEN 1 THEN 'USD'
            WHEN 2 THEN 'EUR'
            WHEN 3 THEN 'GBP'
            WHEN 4 THEN 'JPY'
            ELSE 'USD'
        END,
        'status', CASE (UNIFORM(1, 20, RANDOM()))
            WHEN 1 THEN 'suspended'
            WHEN 2 THEN 'frozen'
            ELSE 'active'
        END,
        'opened_date', DATEADD(day, -UNIFORM(1, 1825, RANDOM()), CURRENT_DATE())::STRING,
        'overdraft_limit', ROUND(UNIFORM(0, 5000, RANDOM()), 2),
        'interest_rate', ROUND(UNIFORM(0.5, 5.5, RANDOM()), 2)
    ) AS PROPS
FROM TABLE(GENERATOR(ROWCOUNT => 25000));

-- Step 3: Generate 20,000 Transaction nodes
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_NODE (NODE_ID, NODE_TYPE, NAME, PROPS)
SELECT
    'TXN' || LPAD(seq4(), 6, '0') AS NODE_ID,
    'Transaction' AS NODE_TYPE,
    CASE (UNIFORM(1, 10, RANDOM()))
        WHEN 1 THEN 'Wire Transfer'
        WHEN 2 THEN 'ACH Payment'
        WHEN 3 THEN 'Card Purchase'
        WHEN 4 THEN 'ATM Withdrawal'
        WHEN 5 THEN 'Mobile Payment'
        WHEN 6 THEN 'Check Deposit'
        WHEN 7 THEN 'Direct Deposit'
        WHEN 8 THEN 'Bill Payment'
        WHEN 9 THEN 'Cash Deposit'
        ELSE 'International Transfer'
    END || ' #' || seq4() AS NAME,
    OBJECT_CONSTRUCT(
        'transaction_id', 'TXN-' || LPAD(seq4(), 12, '0'),
        'amount', ROUND(UNIFORM(10, 50000, RANDOM()), 2),
        'currency', CASE (UNIFORM(1, 5, RANDOM()))
            WHEN 1 THEN 'USD'
            WHEN 2 THEN 'EUR'
            WHEN 3 THEN 'GBP'
            WHEN 4 THEN 'JPY'
            ELSE 'USD'
        END,
        'transaction_type', CASE (UNIFORM(1, 10, RANDOM()))
            WHEN 1 THEN 'wire_transfer'
            WHEN 2 THEN 'ach_payment'
            WHEN 3 THEN 'card_purchase'
            WHEN 4 THEN 'atm_withdrawal'
            WHEN 5 THEN 'mobile_payment'
            WHEN 6 THEN 'check_deposit'
            WHEN 7 THEN 'direct_deposit'
            WHEN 8 THEN 'bill_payment'
            WHEN 9 THEN 'cash_deposit'
            ELSE 'international_transfer'
        END,
        'status', CASE (UNIFORM(1, 20, RANDOM()))
            WHEN 1 THEN 'pending'
            WHEN 2 THEN 'failed'
            WHEN 3 THEN 'flagged'
            ELSE 'completed'
        END,
        'timestamp', DATEADD(minute, -UNIFORM(1, 525600, RANDOM()), CURRENT_TIMESTAMP())::STRING,
        'merchant', CASE (UNIFORM(1, 15, RANDOM()))
            WHEN 1 THEN 'Amazon'
            WHEN 2 THEN 'Walmart'
            WHEN 3 THEN 'Target'
            WHEN 4 THEN 'Starbucks'
            WHEN 5 THEN 'Shell Gas'
            WHEN 6 THEN 'McDonald''s'
            WHEN 7 THEN 'Apple Store'
            WHEN 8 THEN 'Uber'
            WHEN 9 THEN 'Netflix'
            WHEN 10 THEN 'Airlines'
            ELSE 'Various'
        END,
        'location', CASE (UNIFORM(1, 10, RANDOM()))
            WHEN 1 THEN 'New York, NY'
            WHEN 2 THEN 'Los Angeles, CA'
            WHEN 3 THEN 'Chicago, IL'
            WHEN 4 THEN 'Houston, TX'
            WHEN 5 THEN 'Miami, FL'
            WHEN 6 THEN 'London, UK'
            WHEN 7 THEN 'Toronto, CA'
            WHEN 8 THEN 'Tokyo, JP'
            ELSE 'San Francisco, CA'
        END,
        'risk_score', UNIFORM(1, 100, RANDOM())
    ) AS PROPS
FROM TABLE(GENERATOR(ROWCOUNT => 20000));

-- Step 4: Generate 10,000 Device nodes
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_NODE (NODE_ID, NODE_TYPE, NAME, PROPS)
SELECT
    'DEV' || LPAD(seq4(), 6, '0') AS NODE_ID,
    'Device' AS NODE_TYPE,
    CASE (UNIFORM(1, 6, RANDOM()))
        WHEN 1 THEN 'iPhone'
        WHEN 2 THEN 'Android Phone'
        WHEN 3 THEN 'Desktop PC'
        WHEN 4 THEN 'Laptop'
        WHEN 5 THEN 'Tablet'
        ELSE 'Smart Watch'
    END || ' #' || seq4() AS NAME,
    OBJECT_CONSTRUCT(
        'device_id', 'DEV-' || LPAD(seq4(), 10, '0'),
        'device_type', CASE (UNIFORM(1, 6, RANDOM()))
            WHEN 1 THEN 'mobile_ios'
            WHEN 2 THEN 'mobile_android'
            WHEN 3 THEN 'desktop_windows'
            WHEN 4 THEN 'desktop_mac'
            WHEN 5 THEN 'tablet'
            ELSE 'wearable'
        END,
        'ip_address', 
            UNIFORM(1, 255, RANDOM()) || '.' ||
            UNIFORM(1, 255, RANDOM()) || '.' ||
            UNIFORM(1, 255, RANDOM()) || '.' ||
            UNIFORM(1, 255, RANDOM()),
        'os_version', CASE (UNIFORM(1, 6, RANDOM()))
            WHEN 1 THEN 'iOS 17.2'
            WHEN 2 THEN 'Android 14'
            WHEN 3 THEN 'Windows 11'
            WHEN 4 THEN 'macOS 14'
            WHEN 5 THEN 'iPadOS 17'
            ELSE 'watchOS 10'
        END,
        'browser', CASE (UNIFORM(1, 5, RANDOM()))
            WHEN 1 THEN 'Chrome'
            WHEN 2 THEN 'Safari'
            WHEN 3 THEN 'Firefox'
            WHEN 4 THEN 'Edge'
            ELSE 'Mobile App'
        END,
        'first_seen', DATEADD(day, -UNIFORM(1, 730, RANDOM()), CURRENT_DATE())::STRING,
        'last_seen', DATEADD(day, -UNIFORM(1, 30, RANDOM()), CURRENT_DATE())::STRING,
        'is_trusted', UNIFORM(1, 10, RANDOM()) > 2,
        'fingerprint', MD5(seq4()::STRING)
    ) AS PROPS
FROM TABLE(GENERATOR(ROWCOUNT => 10000));

-- Step 5: Generate EDGES - Customer OWNS Account relationships (25,000 edges)
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_EDGE 
(EDGE_ID, SRC_ID, DST_ID, EDGE_TYPE, WEIGHT, PROPS, EFFECTIVE_START)
SELECT
    'EDGE_OWNS_' || LPAD(seq4(), 6, '0') AS EDGE_ID,
    'CUST' || LPAD(UNIFORM(1, 20000, RANDOM()), 6, '0') AS SRC_ID,
    'ACCT' || LPAD(seq4(), 6, '0') AS DST_ID,
    'OWNS' AS EDGE_TYPE,
    1 AS WEIGHT,
    OBJECT_CONSTRUCT(
        'ownership_pct', CASE (UNIFORM(1, 10, RANDOM()))
            WHEN 1 THEN 50
            WHEN 2 THEN 33
            ELSE 100
        END,
        'relationship', CASE (UNIFORM(1, 5, RANDOM()))
            WHEN 1 THEN 'primary_owner'
            WHEN 2 THEN 'joint_owner'
            WHEN 3 THEN 'beneficiary'
            ELSE 'primary_owner'
        END,
        'since', DATEADD(day, -UNIFORM(1, 1825, RANDOM()), CURRENT_DATE())::STRING
    ) AS PROPS,
    DATEADD(day, -UNIFORM(1, 1825, RANDOM()), CURRENT_DATE()) AS EFFECTIVE_START
FROM TABLE(GENERATOR(ROWCOUNT => 25000));

-- Step 6: Generate EDGES - Account TRANSACTED Transaction relationships (20,000 edges)
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_EDGE 
(EDGE_ID, SRC_ID, DST_ID, EDGE_TYPE, WEIGHT, PROPS, EFFECTIVE_START)
SELECT
    'EDGE_TXN_' || LPAD(seq4(), 6, '0') AS EDGE_ID,
    'ACCT' || LPAD(UNIFORM(1, 25000, RANDOM()), 6, '0') AS SRC_ID,
    'TXN' || LPAD(seq4(), 6, '0') AS DST_ID,
    'TRANSACTED' AS EDGE_TYPE,
    UNIFORM(1, 5, RANDOM()) / 10.0 AS WEIGHT,
    OBJECT_CONSTRUCT(
        'direction', CASE (UNIFORM(1, 2, RANDOM()))
            WHEN 1 THEN 'debit'
            ELSE 'credit'
        END,
        'channel', CASE (UNIFORM(1, 6, RANDOM()))
            WHEN 1 THEN 'online'
            WHEN 2 THEN 'mobile'
            WHEN 3 THEN 'atm'
            WHEN 4 THEN 'branch'
            WHEN 5 THEN 'phone'
            ELSE 'api'
        END,
        'processed_by', 'SYSTEM_' || UNIFORM(1, 10, RANDOM())
    ) AS PROPS,
    DATEADD(minute, -UNIFORM(1, 525600, RANDOM()), CURRENT_TIMESTAMP())::DATE AS EFFECTIVE_START
FROM TABLE(GENERATOR(ROWCOUNT => 20000));

-- Step 7: Generate EDGES - Device USED_BY Customer relationships (15,000 edges)
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_EDGE 
(EDGE_ID, SRC_ID, DST_ID, EDGE_TYPE, WEIGHT, PROPS, EFFECTIVE_START)
SELECT
    'EDGE_DEV_' || LPAD(seq4(), 6, '0') AS EDGE_ID,
    'DEV' || LPAD(UNIFORM(1, 10000, RANDOM()), 6, '0') AS SRC_ID,
    'CUST' || LPAD(UNIFORM(1, 20000, RANDOM()), 6, '0') AS DST_ID,
    'USED_BY' AS EDGE_TYPE,
    UNIFORM(5, 10, RANDOM()) / 10.0 AS WEIGHT,
    OBJECT_CONSTRUCT(
        'registration_date', DATEADD(day, -UNIFORM(1, 730, RANDOM()), CURRENT_DATE())::STRING,
        'last_activity', DATEADD(day, -UNIFORM(1, 30, RANDOM()), CURRENT_DATE())::STRING,
        'login_count', UNIFORM(1, 500, RANDOM()),
        'is_primary_device', UNIFORM(1, 5, RANDOM()) = 1
    ) AS PROPS,
    DATEADD(day, -UNIFORM(1, 730, RANDOM()), CURRENT_DATE()) AS EFFECTIVE_START
FROM TABLE(GENERATOR(ROWCOUNT => 15000));

-- Step 8: Generate EDGES - Transaction INITIATED_FROM Device relationships (10,000 edges)
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_EDGE 
(EDGE_ID, SRC_ID, DST_ID, EDGE_TYPE, WEIGHT, PROPS, EFFECTIVE_START)
SELECT
    'EDGE_INIT_' || LPAD(seq4(), 6, '0') AS EDGE_ID,
    'TXN' || LPAD(UNIFORM(1, 20000, RANDOM()), 6, '0') AS SRC_ID,
    'DEV' || LPAD(UNIFORM(1, 10000, RANDOM()), 6, '0') AS DST_ID,
    'INITIATED_FROM' AS EDGE_TYPE,
    1 AS WEIGHT,
    OBJECT_CONSTRUCT(
        'session_id', 'SESSION-' || LPAD(UNIFORM(1, 999999, RANDOM()), 8, '0'),
        'authentication_method', CASE (UNIFORM(1, 5, RANDOM()))
            WHEN 1 THEN 'password'
            WHEN 2 THEN 'biometric'
            WHEN 3 THEN '2fa'
            WHEN 4 THEN 'sms'
            ELSE 'oauth'
        END,
        'geo_location', CASE (UNIFORM(1, 10, RANDOM()))
            WHEN 1 THEN 'US-NY'
            WHEN 2 THEN 'US-CA'
            WHEN 3 THEN 'US-TX'
            WHEN 4 THEN 'GB-LON'
            WHEN 5 THEN 'CA-TOR'
            ELSE 'US-FL'
        END
    ) AS PROPS,
    DATEADD(minute, -UNIFORM(1, 525600, RANDOM()), CURRENT_TIMESTAMP())::DATE AS EFFECTIVE_START
FROM TABLE(GENERATOR(ROWCOUNT => 10000));

-- Step 9: Generate EDGES - Customer REFERRED Customer relationships (3,000 edges for referral network)
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_EDGE 
(EDGE_ID, SRC_ID, DST_ID, EDGE_TYPE, WEIGHT, PROPS, EFFECTIVE_START)
SELECT
    'EDGE_REF_' || LPAD(seq4(), 6, '0') AS EDGE_ID,
    'CUST' || LPAD(UNIFORM(1, 20000, RANDOM()), 6, '0') AS SRC_ID,
    'CUST' || LPAD(UNIFORM(1, 20000, RANDOM()), 6, '0') AS DST_ID,
    'REFERRED' AS EDGE_TYPE,
    UNIFORM(3, 10, RANDOM()) / 10.0 AS WEIGHT,
    OBJECT_CONSTRUCT(
        'referral_code', 'REF-' || LPAD(UNIFORM(1, 9999, RANDOM()), 6, '0'),
        'referral_date', DATEADD(day, -UNIFORM(1, 1095, RANDOM()), CURRENT_DATE())::STRING,
        'bonus_earned', ROUND(UNIFORM(25, 500, RANDOM()), 2),
        'status', CASE (UNIFORM(1, 5, RANDOM()))
            WHEN 1 THEN 'pending'
            ELSE 'completed'
        END
    ) AS PROPS,
    DATEADD(day, -UNIFORM(1, 1095, RANDOM()), CURRENT_DATE()) AS EFFECTIVE_START
FROM TABLE(GENERATOR(ROWCOUNT => 3000));

-- Step 10: Generate EDGES - Account TRANSFERRED_TO Account relationships (5,000 edges for transfers between accounts)
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_EDGE 
(EDGE_ID, SRC_ID, DST_ID, EDGE_TYPE, WEIGHT, PROPS, EFFECTIVE_START)
SELECT
    'EDGE_XFER_' || LPAD(seq4(), 6, '0') AS EDGE_ID,
    'ACCT' || LPAD(UNIFORM(1, 25000, RANDOM()), 6, '0') AS SRC_ID,
    'ACCT' || LPAD(UNIFORM(1, 25000, RANDOM()), 6, '0') AS DST_ID,
    'TRANSFERRED_TO' AS EDGE_TYPE,
    UNIFORM(1, 10, RANDOM()) / 10.0 AS WEIGHT,
    OBJECT_CONSTRUCT(
        'transfer_count', UNIFORM(1, 50, RANDOM()),
        'total_amount', ROUND(UNIFORM(100, 100000, RANDOM()), 2),
        'last_transfer_date', DATEADD(day, -UNIFORM(1, 365, RANDOM()), CURRENT_DATE())::STRING,
        'transfer_type', CASE (UNIFORM(1, 4, RANDOM()))
            WHEN 1 THEN 'internal'
            WHEN 2 THEN 'external'
            WHEN 3 THEN 'wire'
            ELSE 'ach'
        END
    ) AS PROPS,
    DATEADD(day, -UNIFORM(1, 730, RANDOM()), CURRENT_DATE()) AS EFFECTIVE_START
FROM TABLE(GENERATOR(ROWCOUNT => 5000));

-- Generate second batch of 75K sample records for knowledge graph with customers, accounts, transactions, and devices
-- Step 1: Generate 20,000 Customer nodes (Batch 2)
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_NODE (NODE_ID, NODE_TYPE, NAME, PROPS)
SELECT
    'CUST' || LPAD(20000 + seq4(), 6, '0') AS NODE_ID,
    'Customer' AS NODE_TYPE,
    CASE (UNIFORM(1, 20, RANDOM()))
        WHEN 1 THEN 'Amanda Wilson'
        WHEN 2 THEN 'Brandon Miller'
        WHEN 3 THEN 'Christina Lopez'
        WHEN 4 THEN 'Derek Anderson'
        WHEN 5 THEN 'Elizabeth Thomas'
        WHEN 6 THEN 'Frank Martinez'
        WHEN 7 THEN 'Grace Robinson'
        WHEN 8 THEN 'Henry Clark'
        WHEN 9 THEN 'Isabella Rodriguez'
        WHEN 10 THEN 'Jacob Lewis'
        WHEN 11 THEN 'Katherine Walker'
        WHEN 12 THEN 'Leonardo Hall'
        WHEN 13 THEN 'Michelle Allen'
        WHEN 14 THEN 'Nathan Young'
        WHEN 15 THEN 'Olivia King'
        WHEN 16 THEN 'Patrick Wright'
        WHEN 17 THEN 'Quinn Scott'
        WHEN 18 THEN 'Rachel Green'
        WHEN 19 THEN 'Samuel Hill'
        ELSE 'Victoria Adams'
    END || ' ' || (20000 + seq4()) AS NAME,
    OBJECT_CONSTRUCT(
        'email', 'user' || (20000 + seq4()) || '@email.com',
        'kyc_status', CASE UNIFORM(1, 100, RANDOM()) 
            WHEN 93 THEN 'flagged'
            WHEN 94 THEN 'pending'
            ELSE 'verified'
        END,
        'phone', '+1-555-' || LPAD(UNIFORM(5000, 9999, RANDOM()), 4, '0'),
        'registration_date', DATEADD(day, -UNIFORM(1, 1460, RANDOM()), CURRENT_DATE())::STRING,
        'risk_score', UNIFORM(1, 100, RANDOM()),
        'country', CASE (UNIFORM(1, 10, RANDOM()))
            WHEN 1 THEN 'USA'
            WHEN 2 THEN 'Canada'
            WHEN 3 THEN 'Mexico'
            WHEN 4 THEN 'Brazil'
            WHEN 5 THEN 'Spain'
            WHEN 6 THEN 'Italy'
            WHEN 7 THEN 'South Korea'
            WHEN 8 THEN 'India'
            ELSE 'USA'
        END,
        'customer_tier', CASE (UNIFORM(1, 10, RANDOM()))
            WHEN 1 THEN 'platinum'
            WHEN 2 THEN 'gold'
            WHEN 3 THEN 'silver'
            ELSE 'standard'
        END
    ) AS PROPS
FROM TABLE(GENERATOR(ROWCOUNT => 20000));

-- Step 2: Generate 25,000 Account nodes (Batch 2)
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_NODE (NODE_ID, NODE_TYPE, NAME, PROPS)
SELECT
    'ACCT' || LPAD(25000 + seq4(), 6, '0') AS NODE_ID,
    'Account' AS NODE_TYPE,
    CASE (UNIFORM(1, 5, RANDOM()))
        WHEN 1 THEN 'Premium Checking'
        WHEN 2 THEN 'High Yield Savings'
        WHEN 3 THEN 'Corporate Account'
        WHEN 4 THEN 'Retirement Account'
        ELSE 'Premium Credit'
    END || ' #' || (25000 + seq4()) AS NAME,
    OBJECT_CONSTRUCT(
        'account_number', 'ACC-' || LPAD(25000 + seq4(), 10, '0'),
        'account_type', CASE (UNIFORM(1, 5, RANDOM()))
            WHEN 1 THEN 'checking'
            WHEN 2 THEN 'savings'
            WHEN 3 THEN 'business'
            WHEN 4 THEN 'investment'
            ELSE 'credit'
        END,
        'balance', ROUND(UNIFORM(500, 750000, RANDOM()), 2),
        'currency', CASE (UNIFORM(1, 5, RANDOM()))
            WHEN 1 THEN 'USD'
            WHEN 2 THEN 'EUR'
            WHEN 3 THEN 'GBP'
            WHEN 4 THEN 'CAD'
            ELSE 'USD'
        END,
        'status', CASE (UNIFORM(1, 20, RANDOM()))
            WHEN 1 THEN 'suspended'
            WHEN 2 THEN 'frozen'
            ELSE 'active'
        END,
        'opened_date', DATEADD(day, -UNIFORM(1, 1825, RANDOM()), CURRENT_DATE())::STRING,
        'overdraft_limit', ROUND(UNIFORM(0, 10000, RANDOM()), 2),
        'interest_rate', ROUND(UNIFORM(0.25, 6.5, RANDOM()), 2)
    ) AS PROPS
FROM TABLE(GENERATOR(ROWCOUNT => 25000));

-- Step 3: Generate 20,000 Transaction nodes (Batch 2)
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_NODE (NODE_ID, NODE_TYPE, NAME, PROPS)
SELECT
    'TXN' || LPAD(20000 + seq4(), 6, '0') AS NODE_ID,
    'Transaction' AS NODE_TYPE,
    CASE (UNIFORM(1, 10, RANDOM()))
        WHEN 1 THEN 'SWIFT Transfer'
        WHEN 2 THEN 'Zelle Payment'
        WHEN 3 THEN 'Online Purchase'
        WHEN 4 THEN 'Branch Withdrawal'
        WHEN 5 THEN 'Venmo Payment'
        WHEN 6 THEN 'Mobile Check Deposit'
        WHEN 7 THEN 'Payroll Direct Deposit'
        WHEN 8 THEN 'Auto Payment'
        WHEN 9 THEN 'Cash Withdrawal'
        ELSE 'Cross-Border Transfer'
    END || ' #' || (20000 + seq4()) AS NAME,
    OBJECT_CONSTRUCT(
        'transaction_id', 'TXN-' || LPAD(20000 + seq4(), 12, '0'),
        'amount', ROUND(UNIFORM(5, 75000, RANDOM()), 2),
        'currency', CASE (UNIFORM(1, 5, RANDOM()))
            WHEN 1 THEN 'USD'
            WHEN 2 THEN 'EUR'
            WHEN 3 THEN 'GBP'
            WHEN 4 THEN 'CAD'
            ELSE 'USD'
        END,
        'transaction_type', CASE (UNIFORM(1, 10, RANDOM()))
            WHEN 1 THEN 'swift_transfer'
            WHEN 2 THEN 'zelle_payment'
            WHEN 3 THEN 'online_purchase'
            WHEN 4 THEN 'branch_withdrawal'
            WHEN 5 THEN 'venmo_payment'
            WHEN 6 THEN 'mobile_check_deposit'
            WHEN 7 THEN 'payroll_deposit'
            WHEN 8 THEN 'auto_payment'
            WHEN 9 THEN 'cash_withdrawal'
            ELSE 'cross_border_transfer'
        END,
        'status', CASE (UNIFORM(1, 20, RANDOM()))
            WHEN 1 THEN 'pending'
            WHEN 2 THEN 'failed'
            WHEN 3 THEN 'flagged'
            ELSE 'completed'
        END,
        'timestamp', DATEADD(minute, -UNIFORM(1, 525600, RANDOM()), CURRENT_TIMESTAMP())::STRING,
        'merchant', CASE (UNIFORM(1, 15, RANDOM()))
            WHEN 1 THEN 'Best Buy'
            WHEN 2 THEN 'Costco'
            WHEN 3 THEN 'Home Depot'
            WHEN 4 THEN 'Whole Foods'
            WHEN 5 THEN 'Chevron'
            WHEN 6 THEN 'Chipotle'
            WHEN 7 THEN 'Tesla'
            WHEN 8 THEN 'Lyft'
            WHEN 9 THEN 'Spotify'
            WHEN 10 THEN 'Hotels'
            ELSE 'Various'
        END,
        'location', CASE (UNIFORM(1, 10, RANDOM()))
            WHEN 1 THEN 'Seattle, WA'
            WHEN 2 THEN 'Boston, MA'
            WHEN 3 THEN 'Atlanta, GA'
            WHEN 4 THEN 'Dallas, TX'
            WHEN 5 THEN 'Phoenix, AZ'
            WHEN 6 THEN 'Paris, FR'
            WHEN 7 THEN 'Vancouver, CA'
            WHEN 8 THEN 'Seoul, KR'
            ELSE 'Denver, CO'
        END,
        'risk_score', UNIFORM(1, 100, RANDOM())
    ) AS PROPS
FROM TABLE(GENERATOR(ROWCOUNT => 20000));

-- Step 4: Generate 10,000 Device nodes (Batch 2)
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_NODE (NODE_ID, NODE_TYPE, NAME, PROPS)
SELECT
    'DEV' || LPAD(10000 + seq4(), 6, '0') AS NODE_ID,
    'Device' AS NODE_TYPE,
    CASE (UNIFORM(1, 6, RANDOM()))
        WHEN 1 THEN 'Samsung Galaxy'
        WHEN 2 THEN 'Google Pixel'
        WHEN 3 THEN 'MacBook Pro'
        WHEN 4 THEN 'Dell Laptop'
        WHEN 5 THEN 'iPad Pro'
        ELSE 'Fitbit'
    END || ' #' || (10000 + seq4()) AS NAME,
    OBJECT_CONSTRUCT(
        'device_id', 'DEV-' || LPAD(10000 + seq4(), 10, '0'),
        'device_type', CASE (UNIFORM(1, 6, RANDOM()))
            WHEN 1 THEN 'mobile_ios'
            WHEN 2 THEN 'mobile_android'
            WHEN 3 THEN 'desktop_windows'
            WHEN 4 THEN 'desktop_mac'
            WHEN 5 THEN 'tablet'
            ELSE 'wearable'
        END,
        'ip_address', 
            UNIFORM(10, 255, RANDOM()) || '.' ||
            UNIFORM(10, 255, RANDOM()) || '.' ||
            UNIFORM(10, 255, RANDOM()) || '.' ||
            UNIFORM(10, 255, RANDOM()),
        'os_version', CASE (UNIFORM(1, 6, RANDOM()))
            WHEN 1 THEN 'iOS 17.3'
            WHEN 2 THEN 'Android 15'
            WHEN 3 THEN 'Windows 11 Pro'
            WHEN 4 THEN 'macOS 14.2'
            WHEN 5 THEN 'iPadOS 17.3'
            ELSE 'watchOS 10.2'
        END,
        'browser', CASE (UNIFORM(1, 5, RANDOM()))
            WHEN 1 THEN 'Chrome'
            WHEN 2 THEN 'Safari'
            WHEN 3 THEN 'Firefox'
            WHEN 4 THEN 'Brave'
            ELSE 'Mobile App'
        END,
        'first_seen', DATEADD(day, -UNIFORM(1, 730, RANDOM()), CURRENT_DATE())::STRING,
        'last_seen', DATEADD(day, -UNIFORM(1, 30, RANDOM()), CURRENT_DATE())::STRING,
        'is_trusted', UNIFORM(1, 10, RANDOM()) > 3,
        'fingerprint', MD5((10000 + seq4())::STRING)
    ) AS PROPS
FROM TABLE(GENERATOR(ROWCOUNT => 10000));

-- Step 5: Generate EDGES - Customer OWNS Account relationships (25,000 edges, Batch 2)
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_EDGE 
(EDGE_ID, SRC_ID, DST_ID, EDGE_TYPE, WEIGHT, PROPS, EFFECTIVE_START)
SELECT
    'EDGE_OWNS_' || LPAD(25000 + seq4(), 6, '0') AS EDGE_ID,
    'CUST' || LPAD(UNIFORM(20001, 40000, RANDOM()), 6, '0') AS SRC_ID,
    'ACCT' || LPAD(25000 + seq4(), 6, '0') AS DST_ID,
    'OWNS' AS EDGE_TYPE,
    1 AS WEIGHT,
    OBJECT_CONSTRUCT(
        'ownership_pct', CASE (UNIFORM(1, 10, RANDOM()))
            WHEN 1 THEN 50
            WHEN 2 THEN 25
            WHEN 3 THEN 33
            ELSE 100
        END,
        'relationship', CASE (UNIFORM(1, 5, RANDOM()))
            WHEN 1 THEN 'primary_owner'
            WHEN 2 THEN 'joint_owner'
            WHEN 3 THEN 'beneficiary'
            WHEN 4 THEN 'co_signer'
            ELSE 'primary_owner'
        END,
        'since', DATEADD(day, -UNIFORM(1, 1825, RANDOM()), CURRENT_DATE())::STRING
    ) AS PROPS,
    DATEADD(day, -UNIFORM(1, 1825, RANDOM()), CURRENT_DATE()) AS EFFECTIVE_START
FROM TABLE(GENERATOR(ROWCOUNT => 25000));

-- Step 6: Generate EDGES - Account TRANSACTED Transaction relationships (20,000 edges, Batch 2)
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_EDGE 
(EDGE_ID, SRC_ID, DST_ID, EDGE_TYPE, WEIGHT, PROPS, EFFECTIVE_START)
SELECT
    'EDGE_TXN_' || LPAD(20000 + seq4(), 6, '0') AS EDGE_ID,
    'ACCT' || LPAD(UNIFORM(25001, 50000, RANDOM()), 6, '0') AS SRC_ID,
    'TXN' || LPAD(20000 + seq4(), 6, '0') AS DST_ID,
    'TRANSACTED' AS EDGE_TYPE,
    UNIFORM(1, 5, RANDOM()) / 10.0 AS WEIGHT,
    OBJECT_CONSTRUCT(
        'direction', CASE (UNIFORM(1, 2, RANDOM()))
            WHEN 1 THEN 'debit'
            ELSE 'credit'
        END,
        'channel', CASE (UNIFORM(1, 6, RANDOM()))
            WHEN 1 THEN 'online'
            WHEN 2 THEN 'mobile'
            WHEN 3 THEN 'atm'
            WHEN 4 THEN 'branch'
            WHEN 5 THEN 'phone'
            ELSE 'api'
        END,
        'processed_by', 'SYSTEM_' || UNIFORM(11, 20, RANDOM())
    ) AS PROPS,
    DATEADD(minute, -UNIFORM(1, 525600, RANDOM()), CURRENT_TIMESTAMP())::DATE AS EFFECTIVE_START
FROM TABLE(GENERATOR(ROWCOUNT => 20000));

-- Step 7: Generate EDGES - Device USED_BY Customer relationships (15,000 edges, Batch 2)
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_EDGE 
(EDGE_ID, SRC_ID, DST_ID, EDGE_TYPE, WEIGHT, PROPS, EFFECTIVE_START)
SELECT
    'EDGE_DEV_' || LPAD(15000 + seq4(), 6, '0') AS EDGE_ID,
    'DEV' || LPAD(UNIFORM(10001, 20000, RANDOM()), 6, '0') AS SRC_ID,
    'CUST' || LPAD(UNIFORM(20001, 40000, RANDOM()), 6, '0') AS DST_ID,
    'USED_BY' AS EDGE_TYPE,
    UNIFORM(5, 10, RANDOM()) / 10.0 AS WEIGHT,
    OBJECT_CONSTRUCT(
        'registration_date', DATEADD(day, -UNIFORM(1, 730, RANDOM()), CURRENT_DATE())::STRING,
        'last_activity', DATEADD(day, -UNIFORM(1, 30, RANDOM()), CURRENT_DATE())::STRING,
        'login_count', UNIFORM(1, 1000, RANDOM()),
        'is_primary_device', UNIFORM(1, 4, RANDOM()) = 1
    ) AS PROPS,
    DATEADD(day, -UNIFORM(1, 730, RANDOM()), CURRENT_DATE()) AS EFFECTIVE_START
FROM TABLE(GENERATOR(ROWCOUNT => 15000));

-- Step 8: Generate EDGES - Transaction INITIATED_FROM Device relationships (10,000 edges, Batch 2)
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_EDGE 
(EDGE_ID, SRC_ID, DST_ID, EDGE_TYPE, WEIGHT, PROPS, EFFECTIVE_START)
SELECT
    'EDGE_INIT_' || LPAD(10000 + seq4(), 6, '0') AS EDGE_ID,
    'TXN' || LPAD(UNIFORM(20001, 40000, RANDOM()), 6, '0') AS SRC_ID,
    'DEV' || LPAD(UNIFORM(10001, 20000, RANDOM()), 6, '0') AS DST_ID,
    'INITIATED_FROM' AS EDGE_TYPE,
    1 AS WEIGHT,
    OBJECT_CONSTRUCT(
        'session_id', 'SESSION-' || LPAD(UNIFORM(100000, 999999, RANDOM()), 8, '0'),
        'authentication_method', CASE (UNIFORM(1, 5, RANDOM()))
            WHEN 1 THEN 'password'
            WHEN 2 THEN 'biometric'
            WHEN 3 THEN '2fa'
            WHEN 4 THEN 'sms'
            ELSE 'oauth'
        END,
        'geo_location', CASE (UNIFORM(1, 10, RANDOM()))
            WHEN 1 THEN 'US-WA'
            WHEN 2 THEN 'US-MA'
            WHEN 3 THEN 'US-GA'
            WHEN 4 THEN 'FR-PAR'
            WHEN 5 THEN 'CA-VAN'
            ELSE 'US-CO'
        END
    ) AS PROPS,
    DATEADD(minute, -UNIFORM(1, 525600, RANDOM()), CURRENT_TIMESTAMP())::DATE AS EFFECTIVE_START
FROM TABLE(GENERATOR(ROWCOUNT => 10000));

-- Step 9: Generate EDGES - Customer REFERRED Customer relationships (3,000 edges for referral network, Batch 2)
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_EDGE 
(EDGE_ID, SRC_ID, DST_ID, EDGE_TYPE, WEIGHT, PROPS, EFFECTIVE_START)
SELECT
    'EDGE_REF_' || LPAD(3000 + seq4(), 6, '0') AS EDGE_ID,
    'CUST' || LPAD(UNIFORM(20001, 40000, RANDOM()), 6, '0') AS SRC_ID,
    'CUST' || LPAD(UNIFORM(20001, 40000, RANDOM()), 6, '0') AS DST_ID,
    'REFERRED' AS EDGE_TYPE,
    UNIFORM(3, 10, RANDOM()) / 10.0 AS WEIGHT,
    OBJECT_CONSTRUCT(
        'referral_code', 'REF-' || LPAD(UNIFORM(10000, 19999, RANDOM()), 6, '0'),
        'referral_date', DATEADD(day, -UNIFORM(1, 1095, RANDOM()), CURRENT_DATE())::STRING,
        'bonus_earned', ROUND(UNIFORM(50, 750, RANDOM()), 2),
        'status', CASE (UNIFORM(1, 5, RANDOM()))
            WHEN 1 THEN 'pending'
            ELSE 'completed'
        END
    ) AS PROPS,
    DATEADD(day, -UNIFORM(1, 1095, RANDOM()), CURRENT_DATE()) AS EFFECTIVE_START
FROM TABLE(GENERATOR(ROWCOUNT => 3000));

-- Step 10: Generate EDGES - Account TRANSFERRED_TO Account relationships (5,000 edges for transfers, Batch 2)
INSERT INTO A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_EDGE 
(EDGE_ID, SRC_ID, DST_ID, EDGE_TYPE, WEIGHT, PROPS, EFFECTIVE_START)
SELECT
    'EDGE_XFER_' || LPAD(5000 + seq4(), 6, '0') AS EDGE_ID,
    'ACCT' || LPAD(UNIFORM(25001, 50000, RANDOM()), 6, '0') AS SRC_ID,
    'ACCT' || LPAD(UNIFORM(25001, 50000, RANDOM()), 6, '0') AS DST_ID,
    'TRANSFERRED_TO' AS EDGE_TYPE,
    UNIFORM(1, 10, RANDOM()) / 10.0 AS WEIGHT,
    OBJECT_CONSTRUCT(
        'transfer_count', UNIFORM(1, 75, RANDOM()),
        'total_amount', ROUND(UNIFORM(500, 250000, RANDOM()), 2),
        'last_transfer_date', DATEADD(day, -UNIFORM(1, 365, RANDOM()), CURRENT_DATE())::STRING,
        'transfer_type', CASE (UNIFORM(1, 4, RANDOM()))
            WHEN 1 THEN 'internal'
            WHEN 2 THEN 'external'
            WHEN 3 THEN 'wire'
            ELSE 'ach'
        END
    ) AS PROPS,
    DATEADD(day, -UNIFORM(1, 730, RANDOM()), CURRENT_DATE()) AS EFFECTIVE_START
FROM TABLE(GENERATOR(ROWCOUNT => 5000));

-- Verify the record counts (cumulative totals)
SELECT 'Total Nodes' AS metric, COUNT(*) AS count FROM A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_NODE
UNION ALL
SELECT 'Customer Nodes', COUNT(*) FROM A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_NODE WHERE NODE_TYPE = 'Customer'
UNION ALL
SELECT 'Account Nodes', COUNT(*) FROM A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_NODE WHERE NODE_TYPE = 'Account'
UNION ALL
SELECT 'Transaction Nodes', COUNT(*) FROM A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_NODE WHERE NODE_TYPE = 'Transaction'
UNION ALL
SELECT 'Device Nodes', COUNT(*) FROM A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_NODE WHERE NODE_TYPE = 'Device'
UNION ALL
SELECT 'Total Edges', COUNT(*) FROM A01A0E_GBU_FINCRIME_POC.GRAPH_ONTOLOGY.KG_EDGE
ORDER BY metric;
