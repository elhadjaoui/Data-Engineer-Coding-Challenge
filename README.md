# Data-Engineer-Coding-Challenge git add .

# Retrieve country-specific GMV* data, along with corresponding percentages.
```
WITH cte AS (
    SELECT 
        c.id AS country_id,
        c.name AS country_name, 
        o.store_id, 
        s.slug AS store_slug, 
        oi.product_id,
        p.slug AS product_slug, 
        p.price, 
        oi.quantity, 
        o.created_at 
    FROM countries c
    LEFT JOIN stores s ON c.id = s.country_id
    LEFT JOIN orders o ON s.id = o.store_id
    LEFT JOIN order_items oi ON o.id = oi.order_id
    LEFT JOIN products p ON p.id = oi.product_id
),
gmv_total AS (
    SELECT COALESCE(SUM(price * quantity), 0) AS total_gmv
    FROM cte
    WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 YEAR) OR created_at IS NULL -- last year or no sales
)
SELECT 
    country_name,
    COALESCE(SUM(price * quantity), 0) AS GMV,
    CASE 
        WHEN gmv_total.total_gmv > 0 
        THEN CONCAT(ROUND((COALESCE(SUM(price * quantity), 0) * 100) / gmv_total.total_gmv, 2), ' %')
        ELSE '0.00 %'
    END AS percentage
FROM
    cte,
    gmv_total
WHERE
    created_at >= DATE_SUB(NOW(), INTERVAL 1 YEAR) OR created_at IS NULL -- last year or no sales
GROUP BY country_name, gmv_total.total_gmv
ORDER BY GMV DESC;
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
	JOIN
		orders o ON o.store_id = s.id
	JOIN 
		order_items oi ON oi.order_id = o.id 
    JOIN 
		products p ON p.id = oi.product_id
),
gmv_total AS (
    SELECT COALESCE(SUM(price * quantity), 0) AS total_gmv
    FROM
		cte
   WHERE 
		created_at >= DATE_SUB(NOW(), INTERVAL 1 YEAR)  -- last year 
)
SELECT 
    store_id,
    store_name,
    SUM(price * quantity) AS GVM,
    CONCAT(ROUND((SUM(price * quantity) * 100) / gmv_total.total_gmv,2),' %') AS percentage
FROM

    cte,
    gmv_total
WHERE
    created_at >= DATE_SUB(NOW(), INTERVAL 1 YEAR)  -- last year
GROUP BY store_id, store_name, gmv_total.total_gmv
ORDER BY GVM DESC
LIMIT 10 -- top 10 stores
```
