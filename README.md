# Data-Engineer-Coding-Challenge git add .

# Retrieve country-specific GMV* data, along with corresponding percentages.
```
WITH cte AS
(
	SELECT s.country_id, c.name, o.store_id, s.slug as store_slug, product_id,p.slug as product_slug, p.price, quantity, o.created_at 
	FROM orders o
	JOIN order_items oi ON o.id = oi.order_id
	JOIN products p ON p.id = oi.product_id
    JOIN stores s ON s.id = o.store_id
    join countries c on c.id = s.country_id
)
SELECT 
    country_id,
    SUM(price * quantity) AS GVM,
    CONCAT(ROUND((SUM(price * quantity) * 100) 
    / 
    (SELECT SUM(price * quantity) FROM cte WHERE DATEDIFF(NOW(), created_at) <= 365)
    , 2),' %') AS pcnt
FROM
    cte
WHERE
    DATEDIFF(NOW(), created_at) <= 365 -- last year
GROUP BY country_id
ORDER BY GVM DESC
```

# Retrieve top stores with their corresponding GMV

```
WITH cte AS
(
	SELECT  s.id as store_id, 
			s.slug as store_name,
            o.created_at,
            oi.quantity,
            p.price
    FROM 
		stores s
	LEFT JOIN
		orders o ON o.store_id = s.id
	JOIN 
		order_items oi ON oi.order_id = o.id 
    JOIN 
		products p ON p.id = oi.product_id
),
gvm_total AS 
(
	SELECT SUM(price * quantity) AS total_gvm
	FROM cte
    WHERE
		DATEDIFF(NOW(), created_at) <= 365 -- last year
)
SELECT 
    store_id,
    store_name,
    SUM(price * quantity) AS GVM,
    CONCAT(ROUND((SUM(price * quantity) * 100) 
    / 
    (SELECT SUM(price * quantity) FROM cte WHERE DATEDIFF(NOW(), created_at) <= 365), 2),' %') AS percentage
FROM
    cte
WHERE
    DATEDIFF(NOW(), created_at) <= 365 -- last year
GROUP BY store_id, store_name
ORDER BY GVM DESC

```
