-- Compare performance with/without index on orders(status)
CREATE INDEX idx_orders_status ON orders(status);
-- Gather stats
BEGIN DBMS_STATS.GATHER_SCHEMA_STATS(ownname => USER); END;
/
