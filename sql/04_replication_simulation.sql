-- Simple same-DB "replica" schema + trigger-based replication demo
CREATE USER replica IDENTIFIED BY "ReplicaPwd1!";
GRANT CONNECT, RESOURCE TO replica;
ALTER USER replica QUOTA UNLIMITED ON USERS;

-- Replica tables
BEGIN
  FOR t IN (SELECT table_name FROM user_tables) LOOP
    EXECUTE IMMEDIATE 'CREATE TABLE replica.'||t.table_name||' AS SELECT * FROM '||t.table_name||' WHERE 1=0';
  END LOOP;
END;
/

-- Change log and triggers (sample on orders)
CREATE TABLE orders_change_log (
  op VARCHAR2(1), order_id NUMBER, customer_id NUMBER, order_ts TIMESTAMP, status VARCHAR2(20), change_ts TIMESTAMP DEFAULT SYSTIMESTAMP
);

CREATE OR REPLACE TRIGGER trg_orders_log
AFTER INSERT OR UPDATE OR DELETE ON orders
FOR EACH ROW
BEGIN
  IF INSERTING THEN
    INSERT INTO orders_change_log(op, order_id, customer_id, order_ts, status)
    VALUES ('I', :NEW.order_id, :NEW.customer_id, :NEW.order_ts, :NEW.status);
  ELSIF UPDATING THEN
    INSERT INTO orders_change_log(op, order_id, customer_id, order_ts, status)
    VALUES ('U', :NEW.order_id, :NEW.customer_id, :NEW.order_ts, :NEW.status);
  ELSIF DELETING THEN
    INSERT INTO orders_change_log(op, order_id)
    VALUES ('D', :OLD.order_id);
  END IF;
END;
/

-- Apply changes job (periodic)
BEGIN
  DBMS_SCHEDULER.CREATE_JOB (
    job_name        => 'APPLY_REPLICA_CHANGES',
    job_type        => 'PLSQL_BLOCK',
    job_action      => q'[
      DECLARE
        CURSOR c IS SELECT * FROM orders_change_log WHERE change_ts < SYSTIMESTAMP - INTERVAL '5' MINUTE;
      BEGIN
        FOR r IN c LOOP
          IF r.op = 'I' OR r.op='U' THEN
            MERGE INTO replica.orders ro
            USING (SELECT r.order_id oid, r.customer_id cid, r.order_ts ots, r.status st FROM dual) s
            ON (ro.order_id = s.oid)
            WHEN MATCHED THEN UPDATE SET ro.customer_id=s.cid, ro.order_ts=s.ots, ro.status=s.st
            WHEN NOT MATCHED THEN INSERT (order_id, customer_id, order_ts, status) VALUES (s.oid, s.cid, s.ots, s.st);
          ELSIF r.op='D' THEN
            DELETE FROM replica.orders WHERE order_id=r.order_id;
          END IF;
        END LOOP;
        DELETE FROM orders_change_log WHERE change_ts < SYSTIMESTAMP - INTERVAL '5' MINUTE;
        COMMIT;
      END;]',
    start_date      => SYSTIMESTAMP,
    repeat_interval => 'FREQ=MINUTELY;INTERVAL=5',
    enabled         => TRUE
  );
END;
/
