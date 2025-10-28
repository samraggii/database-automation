-- orders_replica table (create if missing)
DECLARE n NUMBER; BEGIN
  SELECT COUNT(*) INTO n FROM user_tables WHERE table_name='ORDERS_REPLICA';
  IF n=0 THEN EXECUTE IMMEDIATE 'CREATE TABLE orders_replica AS SELECT * FROM orders WHERE 1=0'; END IF;
END;
/
-- change log (create if missing)
DECLARE n NUMBER; BEGIN
  SELECT COUNT(*) INTO n FROM user_tables WHERE table_name='ORDERS_CHANGE_LOG';
  IF n=0 THEN
    EXECUTE IMMEDIATE q'[
      CREATE TABLE orders_change_log (
        op         VARCHAR2(1),
        order_id   NUMBER,
        customer_id NUMBER,
        order_ts   TIMESTAMP,
        status     VARCHAR2(20),
        change_ts  TIMESTAMP DEFAULT SYSTIMESTAMP
      )]';
  END IF;
END;
/
-- trigger (always replace so it's fresh)
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
-- job: drop if it exists, then (re)create
BEGIN
  BEGIN DBMS_SCHEDULER.DROP_JOB('APPLY_REPLICA_CHANGES', TRUE); EXCEPTION WHEN OTHERS THEN NULL; END;
  DBMS_SCHEDULER.CREATE_JOB (
    job_name        => 'APPLY_REPLICA_CHANGES',
    job_type        => 'PLSQL_BLOCK',
    job_action      => q'[
      DECLARE
        CURSOR c IS
          SELECT op, order_id, customer_id, order_ts, status
          FROM orders_change_log
          WHERE change_ts < SYSTIMESTAMP - INTERVAL '1' MINUTE;
      BEGIN
        FOR r IN c LOOP
          IF r.op IN ('I','U') THEN
            MERGE INTO orders_replica ro
            USING (SELECT r.order_id oid, r.customer_id cid, r.order_ts ots, r.status st FROM dual) s
            ON (ro.order_id = s.oid)
            WHEN MATCHED THEN UPDATE
              SET ro.customer_id = s.cid, ro.order_ts = s.ots, ro.status = s.st
            WHEN NOT MATCHED THEN INSERT (order_id, customer_id, order_ts, status)
              VALUES (s.oid, s.cid, s.ots, s.st);
          ELSIF r.op = 'D' THEN
            DELETE FROM orders_replica WHERE order_id = r.order_id;
          END IF;
        END LOOP;
        DELETE FROM orders_change_log
         WHERE change_ts < SYSTIMESTAMP - INTERVAL '1' MINUTE;
        COMMIT;
      END;]',
    start_date      => SYSTIMESTAMP,
    repeat_interval => 'FREQ=MINUTELY;INTERVAL=5',
    enabled         => TRUE
  );
END;
/
