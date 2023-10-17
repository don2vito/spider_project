SELECT
	temp_tb."事业部",
	temp_tb.MD名,
	temp_tb."去年销售金额",
	temp_tb."今年销售金额",
	temp_tb."去年销售利润",
	temp_tb."今年销售利润",
	concat ( round(( temp_tb."今年销售金额" / temp_tb."去年销售金额" - 1 ) :: NUMERIC * 100 ), '%' ) AS 销售金额同比,
	concat ( round(( temp_tb."今年销售利润" / temp_tb."去年销售利润" - 1 ) :: NUMERIC * 100 ), '%' ) AS 销售利润同比 
FROM
	(
SELECT
	"数据源"."新事业部" AS 事业部,
	"数据源"."MD名" AS MD名,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售利润" ELSE NULL END ) AS 去年销售利润,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售利润" ELSE NULL END ) AS 今年销售利润 
FROM
	"数据源" 
WHERE
	"数据源"."公司" IN ( '电视购物公司', '旅行社' ) 
GROUP BY
	"数据源"."新事业部",
	"数据源"."MD名" 
	) AS temp_tb 
WHERE
	temp_tb."事业部" = '厨具厨电部' 
	AND temp_tb."去年销售金额" <> 0 
	AND concat ( round(( temp_tb."今年销售金额" / temp_tb."去年销售金额" - 1 ) :: NUMERIC * 100 ), '%' ) <> '%';



SELECT
	temp_tb."事业部",
	temp_tb.MD名,
	temp_tb."去年销售金额",
	temp_tb."今年销售金额",
	temp_tb."去年销售利润",
	temp_tb."今年销售利润",
	concat ( round(( temp_tb."今年销售金额" / temp_tb."去年销售金额" - 1 ) :: NUMERIC * 100 ), '%' ) AS 销售金额同比,
	concat ( round(( temp_tb."今年销售利润" / temp_tb."去年销售利润" - 1 ) :: NUMERIC * 100 ), '%' ) AS 销售利润同比 
FROM
	(
SELECT
	"数据源"."新事业部" AS 事业部,
	"数据源"."MD名" AS MD名,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售利润" ELSE NULL END ) AS 去年销售利润,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售利润" ELSE NULL END ) AS 今年销售利润 
FROM
	"数据源" 
WHERE
	"数据源"."公司" IN ( '电视购物公司', '旅行社' ) 
GROUP BY
	"数据源"."新事业部",
	"数据源"."MD名" 
	) AS temp_tb 
WHERE
	temp_tb."事业部" = '家庭投资部' 
	AND temp_tb."去年销售金额" <> 0 
	AND concat ( round(( temp_tb."今年销售金额" / temp_tb."去年销售金额" - 1 ) :: NUMERIC * 100 ), '%' ) <> '%';
	
	
	
	SELECT
	temp_tb."事业部",
	temp_tb.MD名,
	temp_tb."去年销售金额",
	temp_tb."今年销售金额",
	temp_tb."去年销售利润",
	temp_tb."今年销售利润",
	concat ( round(( temp_tb."今年销售金额" / temp_tb."去年销售金额" - 1 ) :: NUMERIC * 100 ), '%' ) AS 销售金额同比,
	concat ( round(( temp_tb."今年销售利润" / temp_tb."去年销售利润" - 1 ) :: NUMERIC * 100 ), '%' ) AS 销售利润同比 
FROM
	(
SELECT
	"数据源"."新事业部" AS 事业部,
	"数据源"."MD名" AS MD名,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售利润" ELSE NULL END ) AS 去年销售利润,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售利润" ELSE NULL END ) AS 今年销售利润 
FROM
	"数据源" 
WHERE
	"数据源"."公司" IN ( '电视购物公司', '旅行社' ) 
GROUP BY
	"数据源"."新事业部",
	"数据源"."MD名" 
	) AS temp_tb 
WHERE
	temp_tb."事业部" = '健康保健部' 
	AND temp_tb."去年销售金额" <> 0 
	AND concat ( round(( temp_tb."今年销售金额" / temp_tb."去年销售金额" - 1 ) :: NUMERIC * 100 ), '%' ) <> '%';
	
	
	
	SELECT
	temp_tb."事业部",
	temp_tb.MD名,
	temp_tb."去年销售金额",
	temp_tb."今年销售金额",
	temp_tb."去年销售利润",
	temp_tb."今年销售利润",
	concat ( round(( temp_tb."今年销售金额" / temp_tb."去年销售金额" - 1 ) :: NUMERIC * 100 ), '%' ) AS 销售金额同比,
	concat ( round(( temp_tb."今年销售利润" / temp_tb."去年销售利润" - 1 ) :: NUMERIC * 100 ), '%' ) AS 销售利润同比 
FROM
	(
SELECT
	"数据源"."新事业部" AS 事业部,
	"数据源"."MD名" AS MD名,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售利润" ELSE NULL END ) AS 去年销售利润,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售利润" ELSE NULL END ) AS 今年销售利润 
FROM
	"数据源" 
WHERE
	"数据源"."公司" IN ( '电视购物公司', '旅行社' ) 
GROUP BY
	"数据源"."新事业部",
	"数据源"."MD名" 
	) AS temp_tb 
WHERE
	temp_tb."事业部" = '流行服饰部' 
	AND temp_tb."去年销售金额" <> 0 
	AND concat ( round(( temp_tb."今年销售金额" / temp_tb."去年销售金额" - 1 ) :: NUMERIC * 100 ), '%' ) <> '%';
	
	
	
	SELECT
	temp_tb."事业部",
	temp_tb.MD名,
	temp_tb."去年销售金额",
	temp_tb."今年销售金额",
	temp_tb."去年销售利润",
	temp_tb."今年销售利润",
	concat ( round(( temp_tb."今年销售金额" / temp_tb."去年销售金额" - 1 ) :: NUMERIC * 100 ), '%' ) AS 销售金额同比,
	concat ( round(( temp_tb."今年销售利润" / temp_tb."去年销售利润" - 1 ) :: NUMERIC * 100 ), '%' ) AS 销售利润同比 
FROM
	(
SELECT
	"数据源"."新事业部" AS 事业部,
	"数据源"."MD名" AS MD名,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售利润" ELSE NULL END ) AS 去年销售利润,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售利润" ELSE NULL END ) AS 今年销售利润 
FROM
	"数据源" 
WHERE
	"数据源"."公司" IN ( '电视购物公司', '旅行社' ) 
GROUP BY
	"数据源"."新事业部",
	"数据源"."MD名" 
	) AS temp_tb 
WHERE
	temp_tb."事业部" = '生活美食部' 
	AND temp_tb."去年销售金额" <> 0 
	AND concat ( round(( temp_tb."今年销售金额" / temp_tb."去年销售金额" - 1 ) :: NUMERIC * 100 ), '%' ) <> '%';
	
	
	
	SELECT
	temp_tb."事业部",
	temp_tb.MD名,
	temp_tb."去年销售金额",
	temp_tb."今年销售金额",
	temp_tb."去年销售利润",
	temp_tb."今年销售利润",
	concat ( round(( temp_tb."今年销售金额" / temp_tb."去年销售金额" - 1 ) :: NUMERIC * 100 ), '%' ) AS 销售金额同比,
	concat ( round(( temp_tb."今年销售利润" / temp_tb."去年销售利润" - 1 ) :: NUMERIC * 100 ), '%' ) AS 销售利润同比 
FROM
	(
SELECT
	"数据源"."新事业部" AS 事业部,
	"数据源"."MD名" AS MD名,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售利润" ELSE NULL END ) AS 去年销售利润,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售利润" ELSE NULL END ) AS 今年销售利润 
FROM
	"数据源" 
WHERE
	"数据源"."公司" IN ( '电视购物公司', '旅行社' ) 
GROUP BY
	"数据源"."新事业部",
	"数据源"."MD名" 
	) AS temp_tb 
WHERE
	temp_tb."事业部" = '箱包配饰部' 
	AND temp_tb."去年销售金额" <> 0 
	AND concat ( round(( temp_tb."今年销售金额" / temp_tb."去年销售金额" - 1 ) :: NUMERIC * 100 ), '%' ) <> '%';
	
	
	
	SELECT
	temp_tb."事业部",
	temp_tb.MD名,
	temp_tb."去年销售金额",
	temp_tb."今年销售金额",
	temp_tb."去年销售利润",
	temp_tb."今年销售利润",
	concat ( round(( temp_tb."今年销售金额" / temp_tb."去年销售金额" - 1 ) :: NUMERIC * 100 ), '%' ) AS 销售金额同比,
	concat ( round(( temp_tb."今年销售利润" / temp_tb."去年销售利润" - 1 ) :: NUMERIC * 100 ), '%' ) AS 销售利润同比 
FROM
	(
SELECT
	"数据源"."新事业部" AS 事业部,
	"数据源"."MD名" AS MD名,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售利润" ELSE NULL END ) AS 去年销售利润,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售利润" ELSE NULL END ) AS 今年销售利润 
FROM
	"数据源" 
WHERE
	"数据源"."公司" IN ( '电视购物公司', '旅行社' ) 
GROUP BY
	"数据源"."新事业部",
	"数据源"."MD名" 
	) AS temp_tb 
WHERE
	temp_tb."事业部" = '消费服务部' 
	AND temp_tb."去年销售金额" <> 0 
	AND concat ( round(( temp_tb."今年销售金额" / temp_tb."去年销售金额" - 1 ) :: NUMERIC * 100 ), '%' ) <> '%';
	
	
	
	SELECT
	temp_tb."事业部",
	temp_tb.MD名,
	temp_tb."去年销售金额",
	temp_tb."今年销售金额",
	temp_tb."去年销售利润",
	temp_tb."今年销售利润",
	concat ( round(( temp_tb."今年销售金额" / temp_tb."去年销售金额" - 1 ) :: NUMERIC * 100 ), '%' ) AS 销售金额同比,
	concat ( round(( temp_tb."今年销售利润" / temp_tb."去年销售利润" - 1 ) :: NUMERIC * 100 ), '%' ) AS 销售利润同比 
FROM
	(
SELECT
	"数据源"."新事业部" AS 事业部,
	"数据源"."MD名" AS MD名,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售利润" ELSE NULL END ) AS 去年销售利润,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售利润" ELSE NULL END ) AS 今年销售利润 
FROM
	"数据源" 
WHERE
	"数据源"."公司" IN ( '电视购物公司', '旅行社' ) 
GROUP BY
	"数据源"."新事业部",
	"数据源"."MD名" 
	) AS temp_tb 
WHERE
	temp_tb."事业部" = '电子电器部' 
	AND temp_tb."去年销售金额" <> 0 
	AND concat ( round(( temp_tb."今年销售金额" / temp_tb."去年销售金额" - 1 ) :: NUMERIC * 100 ), '%' ) <> '%';
	
	
	
	SELECT
	temp_tb."事业部",
	temp_tb.MD名,
	temp_tb."去年销售金额",
	temp_tb."今年销售金额",
	temp_tb."去年销售利润",
	temp_tb."今年销售利润",
	concat ( round(( temp_tb."今年销售金额" / temp_tb."去年销售金额" - 1 ) :: NUMERIC * 100 ), '%' ) AS 销售金额同比,
	concat ( round(( temp_tb."今年销售利润" / temp_tb."去年销售利润" - 1 ) :: NUMERIC * 100 ), '%' ) AS 销售利润同比 
FROM
	(
SELECT
	"数据源"."新事业部" AS 事业部,
	"数据源"."MD名" AS MD名,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售利润" ELSE NULL END ) AS 去年销售利润,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售利润" ELSE NULL END ) AS 今年销售利润 
FROM
	"数据源" 
WHERE
	"数据源"."公司" IN ( '电视购物公司', '旅行社' ) 
GROUP BY
	"数据源"."新事业部",
	"数据源"."MD名" 
	) AS temp_tb 
WHERE
	temp_tb."事业部" = '家居家纺部' 
	AND temp_tb."去年销售金额" <> 0 
	AND concat ( round(( temp_tb."今年销售金额" / temp_tb."去年销售金额" - 1 ) :: NUMERIC * 100 ), '%' ) <> '%';
	
	
	
	SELECT
	temp_tb."事业部",
	temp_tb.MD名,
	temp_tb."去年销售金额",
	temp_tb."今年销售金额",
	temp_tb."去年销售利润",
	temp_tb."今年销售利润",
	concat ( round(( temp_tb."今年销售金额" / temp_tb."去年销售金额" - 1 ) :: NUMERIC * 100 ), '%' ) AS 销售金额同比,
	concat ( round(( temp_tb."今年销售利润" / temp_tb."去年销售利润" - 1 ) :: NUMERIC * 100 ), '%' ) AS 销售利润同比 
FROM
	(
SELECT
	"数据源"."新事业部" AS 事业部,
	"数据源"."MD名" AS MD名,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售利润" ELSE NULL END ) AS 去年销售利润,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售利润" ELSE NULL END ) AS 今年销售利润 
FROM
	"数据源" 
WHERE
	"数据源"."公司" IN ( '电视购物公司', '旅行社' ) 
GROUP BY
	"数据源"."新事业部",
	"数据源"."MD名" 
	) AS temp_tb 
WHERE
	temp_tb."事业部" = '家装家饰部' 
	AND temp_tb."去年销售金额" <> 0 
	AND concat ( round(( temp_tb."今年销售金额" / temp_tb."去年销售金额" - 1 ) :: NUMERIC * 100 ), '%' ) <> '%';
	
	
	
	SELECT
	temp_tb."事业部",
	temp_tb.MD名,
	temp_tb."去年销售金额",
	temp_tb."今年销售金额",
	temp_tb."去年销售利润",
	temp_tb."今年销售利润",
	concat ( round(( temp_tb."今年销售金额" / temp_tb."去年销售金额" - 1 ) :: NUMERIC * 100 ), '%' ) AS 销售金额同比,
	concat ( round(( temp_tb."今年销售利润" / temp_tb."去年销售利润" - 1 ) :: NUMERIC * 100 ), '%' ) AS 销售利润同比 
FROM
	(
SELECT
	"数据源"."新事业部" AS 事业部,
	"数据源"."MD名" AS MD名,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售利润" ELSE NULL END ) AS 去年销售利润,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售利润" ELSE NULL END ) AS 今年销售利润 
FROM
	"数据源" 
WHERE
	"数据源"."公司" IN ( '电视购物公司', '旅行社' ) 
GROUP BY
	"数据源"."新事业部",
	"数据源"."MD名" 
	) AS temp_tb 
WHERE
	temp_tb."事业部" = '美妆护理部' 
	AND temp_tb."去年销售金额" <> 0 
	AND concat ( round(( temp_tb."今年销售金额" / temp_tb."去年销售金额" - 1 ) :: NUMERIC * 100 ), '%' ) <> '%';
	
	
	
	SELECT
	temp_tb."事业部",
	temp_tb.MD名,
	temp_tb."去年销售金额",
	temp_tb."今年销售金额",
	temp_tb."去年销售利润",
	temp_tb."今年销售利润",
	concat ( round(( temp_tb."今年销售金额" / temp_tb."去年销售金额" - 1 ) :: NUMERIC * 100 ), '%' ) AS 销售金额同比,
	concat ( round(( temp_tb."今年销售利润" / temp_tb."去年销售利润" - 1 ) :: NUMERIC * 100 ), '%' ) AS 销售利润同比 
FROM
	(
SELECT
	"数据源"."新事业部" AS 事业部,
	"数据源"."MD名" AS MD名,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售利润" ELSE NULL END ) AS 去年销售利润,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售利润" ELSE NULL END ) AS 今年销售利润 
FROM
	"数据源" 
WHERE
	"数据源"."公司" IN ( '电视购物公司', '旅行社' ) 
GROUP BY
	"数据源"."新事业部",
	"数据源"."MD名" 
	) AS temp_tb 
WHERE
	temp_tb."事业部" = '生活日用品部' 
	AND temp_tb."去年销售金额" <> 0 
	AND concat ( round(( temp_tb."今年销售金额" / temp_tb."去年销售金额" - 1 ) :: NUMERIC * 100 ), '%' ) <> '%';
	
	
	
	SELECT
	temp_tb."事业部",
	temp_tb.MD名,
	temp_tb."去年销售金额",
	temp_tb."今年销售金额",
	temp_tb."去年销售利润",
	temp_tb."今年销售利润",
	concat ( round(( temp_tb."今年销售金额" / temp_tb."去年销售金额" - 1 ) :: NUMERIC * 100 ), '%' ) AS 销售金额同比,
	concat ( round(( temp_tb."今年销售利润" / temp_tb."去年销售利润" - 1 ) :: NUMERIC * 100 ), '%' ) AS 销售利润同比 
FROM
	(
SELECT
	"数据源"."新事业部" AS 事业部,
	"数据源"."MD名" AS MD名,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售利润" ELSE NULL END ) AS 去年销售利润,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售利润" ELSE NULL END ) AS 今年销售利润 
FROM
	"数据源" 
WHERE
	"数据源"."公司" IN ( '电视购物公司', '旅行社' ) 
GROUP BY
	"数据源"."新事业部",
	"数据源"."MD名" 
	) AS temp_tb 
WHERE
	temp_tb."事业部" = '艺术品交易部' 
	AND temp_tb."去年销售金额" <> 0 
	AND concat ( round(( temp_tb."今年销售金额" / temp_tb."去年销售金额" - 1 ) :: NUMERIC * 100 ), '%' ) <> '%';
	
	
	
	SELECT
	temp_tb."事业部",
	temp_tb.MD名,
	temp_tb."去年销售金额",
	temp_tb."今年销售金额",
	temp_tb."去年销售利润",
	temp_tb."今年销售利润",
	concat ( round(( temp_tb."今年销售金额" / temp_tb."去年销售金额" - 1 ) :: NUMERIC * 100 ), '%' ) AS 销售金额同比,
	concat ( round(( temp_tb."今年销售利润" / temp_tb."去年销售利润" - 1 ) :: NUMERIC * 100 ), '%' ) AS 销售利润同比 
FROM
	(
SELECT
	"数据源"."新事业部" AS 事业部,
	"数据源"."MD名" AS MD名,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售利润" ELSE NULL END ) AS 去年销售利润,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售利润" ELSE NULL END ) AS 今年销售利润 
FROM
	"数据源" 
WHERE
	"数据源"."公司" IN ( '电视购物公司', '旅行社' ) 
GROUP BY
	"数据源"."新事业部",
	"数据源"."MD名" 
	) AS temp_tb 
WHERE
	temp_tb."事业部" = '珠宝饰品部' 
	AND temp_tb."去年销售金额" <> 0 
	AND concat ( round(( temp_tb."今年销售金额" / temp_tb."去年销售金额" - 1 ) :: NUMERIC * 100 ), '%' ) <> '%';