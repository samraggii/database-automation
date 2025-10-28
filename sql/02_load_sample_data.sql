INSERT INTO products(name, price, category)
SELECT 'Item '||LEVEL, ROUND(DBMS_RANDOM.VALUE(5,150),2),
       CASE MOD(LEVEL,4) WHEN 0 THEN 'Home' WHEN 1 THEN 'Tech' WHEN 2 THEN 'Grocery' ELSE 'Clothes' END
FROM dual CONNECT BY LEVEL <= 1000;

INSERT INTO customers(name, email, city)
SELECT 'Customer '||LEVEL, 'user'||LEVEL||'@example.com',
       CASE MOD(LEVEL,5) WHEN 0 THEN 'Dallas' WHEN 1 THEN 'Austin' WHEN 2 THEN 'Houston' WHEN 3 THEN 'Plano' ELSE 'Irving' END
FROM dual CONNECT BY LEVEL <= 10000;

-- Generate orders + items
BEGIN
  FOR i IN 1..50000 LOOP
    INSERT INTO orders(customer_id, status) VALUES (TRUNC(DBMS_RANDOM.VALUE(1,10000)), 'PLACED');
    INSERT INTO order_items(order_id, product_id, qty, price)
      SELECT i, TRUNC(DBMS_RANDOM.VALUE(1,1000)), TRUNC(DBMS_RANDOM.VALUE(1,5)),
             ROUND(DBMS_RANDOM.VALUE(5,150),2) FROM dual CONNECT BY LEVEL <= TRUNC(DBMS_RANDOM.VALUE(1,4));
    IF MOD(i, 1000) = 0 THEN COMMIT; END IF;
  END LOOP;
  COMMIT;
END;
/
