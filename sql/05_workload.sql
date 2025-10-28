-- Hot query (run repeatedly in tests to simulate load)
SELECT c.city, COUNT(*) cnt
FROM orders o JOIN customers c ON o.customer_id=c.customer_id
WHERE o.order_ts >= SYSTIMESTAMP - INTERVAL '7' DAY
GROUP BY c.city
ORDER BY cnt DESC;
