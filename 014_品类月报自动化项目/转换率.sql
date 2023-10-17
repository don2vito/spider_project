SELECT
	temp_tb."事业部",
	temp_tb."区分",
	(
CASE
	
	WHEN temp_tb."区分" LIKE'%部' THEN
	1 
	WHEN temp_tb."区分" = 'TV商品' THEN
	2 
	WHEN temp_tb."区分" = 'IC商品' THEN
	3 
	WHEN temp_tb."区分" = 'TV' THEN
	4 
	WHEN temp_tb."区分" = '新媒体' THEN
	5 
	WHEN temp_tb."区分" = 'CTL' THEN
	6 
END 
	) AS 排序
	,
	concat ( round(( temp_tb."去年销售金额" / temp_tb."去年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 去年转化率,
	concat ( round(( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 今年转化率,
	concat (
		round((( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) - ( temp_tb."去年销售金额" / temp_tb."去年订购金额" )) :: NUMERIC * 100 ),
		'%' 
	) AS 差异 
FROM
	(
	SELECT
		"数据源"."新事业部" AS 事业部,
		"数据源"."新事业部" AS 区分,
		SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
		SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
		SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
		SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
	FROM
		"数据源" 
	WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
	GROUP BY
		"数据源"."新事业部",
		"数据源"."新事业部" UNION ALL
	SELECT
		"数据源"."新事业部" AS 事业部,
		"数据源"."商品区分" AS 区分,
		SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
		SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
		SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
		SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
	FROM
		"数据源" 
	WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
	GROUP BY
		"数据源"."新事业部",
		"数据源"."商品区分" UNION ALL
	SELECT
		"数据源"."新事业部" AS 事业部,
		"数据源"."渠道" AS 区分,
		SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
		SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
		SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
		SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
	FROM
		"数据源" 
	WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
	GROUP BY
		"数据源"."新事业部",
		"数据源"."渠道" 
	) AS temp_tb 
WHERE
	temp_tb."事业部" = '厨具厨电部' 
ORDER BY
	排序;
	
	
	
SELECT
	temp_tb."事业部",
	temp_tb."区分",
	(
	CASE
			
			WHEN temp_tb."区分" LIKE'%部' THEN
			1 
			WHEN temp_tb."区分" = 'TV商品' THEN
			2 
			WHEN temp_tb."区分" = 'IC商品' THEN
			3 
			WHEN temp_tb."区分" = 'TV' THEN
			4 
			WHEN temp_tb."区分" = '新媒体' THEN
			5 
			WHEN temp_tb."区分" = 'CTL' THEN
			6 
		END 
		) AS 排序
		,
		concat ( round(( temp_tb."去年销售金额" / temp_tb."去年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 去年转化率,
		concat ( round(( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 今年转化率,
		concat (
			round((( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) - ( temp_tb."去年销售金额" / temp_tb."去年订购金额" )) :: NUMERIC * 100 ),
			'%' 
		) AS 差异 
	FROM
		(
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."新事业部" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源" 
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
		GROUP BY
			"数据源"."新事业部",
			"数据源"."新事业部" UNION ALL
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."商品区分" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源" 
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
		GROUP BY
			"数据源"."新事业部",
			"数据源"."商品区分" UNION ALL
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."渠道" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源" 
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
		GROUP BY
			"数据源"."新事业部",
			"数据源"."渠道" 
		) AS temp_tb 
	WHERE
		temp_tb."事业部" = '家庭投资部' 
ORDER BY
排序;
	
	
	
SELECT
	temp_tb."事业部",
	temp_tb."区分",
	(
	CASE
			
			WHEN temp_tb."区分" LIKE'%部' THEN
			1 
			WHEN temp_tb."区分" = 'TV商品' THEN
			2 
			WHEN temp_tb."区分" = 'IC商品' THEN
			3 
			WHEN temp_tb."区分" = 'TV' THEN
			4 
			WHEN temp_tb."区分" = '新媒体' THEN
			5 
			WHEN temp_tb."区分" = 'CTL' THEN
			6 
		END 
		) AS 排序
		,
		concat ( round(( temp_tb."去年销售金额" / temp_tb."去年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 去年转化率,
		concat ( round(( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 今年转化率,
		concat (
			round((( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) - ( temp_tb."去年销售金额" / temp_tb."去年订购金额" )) :: NUMERIC * 100 ),
			'%' 
		) AS 差异 
	FROM
		(
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."新事业部" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源" 
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
		GROUP BY
			"数据源"."新事业部",
			"数据源"."新事业部" UNION ALL
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."商品区分" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源" 
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
		GROUP BY
			"数据源"."新事业部",
			"数据源"."商品区分" UNION ALL
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."渠道" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源" 
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
		GROUP BY
			"数据源"."新事业部",
			"数据源"."渠道" 
		) AS temp_tb 
	WHERE
		temp_tb."事业部" = '健康保健部' 
ORDER BY
排序;
	
	
	
SELECT
	temp_tb."事业部",
	temp_tb."区分",
	(
	CASE
			
			WHEN temp_tb."区分" LIKE'%部' THEN
			1 
			WHEN temp_tb."区分" = 'TV商品' THEN
			2 
			WHEN temp_tb."区分" = 'IC商品' THEN
			3 
			WHEN temp_tb."区分" = 'TV' THEN
			4 
			WHEN temp_tb."区分" = '新媒体' THEN
			5 
			WHEN temp_tb."区分" = 'CTL' THEN
			6 
		END 
		) AS 排序
		,
		concat ( round(( temp_tb."去年销售金额" / temp_tb."去年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 去年转化率,
		concat ( round(( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 今年转化率,
		concat (
			round((( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) - ( temp_tb."去年销售金额" / temp_tb."去年订购金额" )) :: NUMERIC * 100 ),
			'%' 
		) AS 差异 
	FROM
		(
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."新事业部" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源"
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')	
		GROUP BY
			"数据源"."新事业部",
			"数据源"."新事业部" UNION ALL
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."商品区分" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源" 
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
		GROUP BY
			"数据源"."新事业部",
			"数据源"."商品区分" UNION ALL
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."渠道" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源" 
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
		GROUP BY
			"数据源"."新事业部",
			"数据源"."渠道" 
		) AS temp_tb 
	WHERE
		temp_tb."事业部" = '流行服饰部' 
ORDER BY
排序;
	
	
	
SELECT
	temp_tb."事业部",
	temp_tb."区分",
	(
	CASE
			
			WHEN temp_tb."区分" LIKE'%部' THEN
			1 
			WHEN temp_tb."区分" = 'TV商品' THEN
			2 
			WHEN temp_tb."区分" = 'IC商品' THEN
			3 
			WHEN temp_tb."区分" = 'TV' THEN
			4 
			WHEN temp_tb."区分" = '新媒体' THEN
			5 
			WHEN temp_tb."区分" = 'CTL' THEN
			6 
		END 
		) AS 排序
		,
		concat ( round(( temp_tb."去年销售金额" / temp_tb."去年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 去年转化率,
		concat ( round(( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 今年转化率,
		concat (
			round((( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) - ( temp_tb."去年销售金额" / temp_tb."去年订购金额" )) :: NUMERIC * 100 ),
			'%' 
		) AS 差异 
	FROM
		(
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."新事业部" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源" 
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
		GROUP BY
			"数据源"."新事业部",
			"数据源"."新事业部" UNION ALL
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."商品区分" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源" 
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
		GROUP BY
			"数据源"."新事业部",
			"数据源"."商品区分" UNION ALL
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."渠道" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源" 
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
		GROUP BY
			"数据源"."新事业部",
			"数据源"."渠道" 
		) AS temp_tb 
	WHERE
		temp_tb."事业部" = '生活美食部' 
ORDER BY
排序;
	
	
	
SELECT
	temp_tb."事业部",
	temp_tb."区分",
	(
	CASE
			
			WHEN temp_tb."区分" LIKE'%部' THEN
			1 
			WHEN temp_tb."区分" = 'TV商品' THEN
			2 
			WHEN temp_tb."区分" = 'IC商品' THEN
			3 
			WHEN temp_tb."区分" = 'TV' THEN
			4 
			WHEN temp_tb."区分" = '新媒体' THEN
			5 
			WHEN temp_tb."区分" = 'CTL' THEN
			6 
		END 
		) AS 排序
		,
		concat ( round(( temp_tb."去年销售金额" / temp_tb."去年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 去年转化率,
		concat ( round(( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 今年转化率,
		concat (
			round((( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) - ( temp_tb."去年销售金额" / temp_tb."去年订购金额" )) :: NUMERIC * 100 ),
			'%' 
		) AS 差异 
	FROM
		(
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."新事业部" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源" 
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
		GROUP BY
			"数据源"."新事业部",
			"数据源"."新事业部" UNION ALL
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."商品区分" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源" 
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
		GROUP BY
			"数据源"."新事业部",
			"数据源"."商品区分" UNION ALL
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."渠道" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源"
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')	
		GROUP BY
			"数据源"."新事业部",
			"数据源"."渠道" 
		) AS temp_tb 
	WHERE
		temp_tb."事业部" = '箱包配饰部' 
ORDER BY
排序;
	
	
	
SELECT
	temp_tb."事业部",
	temp_tb."区分",
	(
	CASE
			
			WHEN temp_tb."区分" LIKE'%部' THEN
			1 
			WHEN temp_tb."区分" = 'TV商品' THEN
			2 
			WHEN temp_tb."区分" = 'IC商品' THEN
			3 
			WHEN temp_tb."区分" = 'TV' THEN
			4 
			WHEN temp_tb."区分" = '新媒体' THEN
			5 
			WHEN temp_tb."区分" = 'CTL' THEN
			6 
		END 
		) AS 排序
		,
		concat ( round(( temp_tb."去年销售金额" / temp_tb."去年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 去年转化率,
		concat ( round(( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 今年转化率,
		concat (
			round((( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) - ( temp_tb."去年销售金额" / temp_tb."去年订购金额" )) :: NUMERIC * 100 ),
			'%' 
		) AS 差异 
	FROM
		(
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."新事业部" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源" 
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
		GROUP BY
			"数据源"."新事业部",
			"数据源"."新事业部" UNION ALL
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."商品区分" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源" 
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
		GROUP BY
			"数据源"."新事业部",
			"数据源"."商品区分" UNION ALL
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."渠道" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源"
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')	
		GROUP BY
			"数据源"."新事业部",
			"数据源"."渠道" 
		) AS temp_tb 
	WHERE
		temp_tb."事业部" = '消费服务部' 
ORDER BY
排序;
	
	
	
SELECT
	temp_tb."事业部",
	temp_tb."区分",
	(
	CASE
			
			WHEN temp_tb."区分" LIKE'%部' THEN
			1 
			WHEN temp_tb."区分" = 'TV商品' THEN
			2 
			WHEN temp_tb."区分" = 'IC商品' THEN
			3 
			WHEN temp_tb."区分" = 'TV' THEN
			4 
			WHEN temp_tb."区分" = '新媒体' THEN
			5 
			WHEN temp_tb."区分" = 'CTL' THEN
			6 
		END 
		) AS 排序
		,
		concat ( round(( temp_tb."去年销售金额" / temp_tb."去年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 去年转化率,
		concat ( round(( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 今年转化率,
		concat (
			round((( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) - ( temp_tb."去年销售金额" / temp_tb."去年订购金额" )) :: NUMERIC * 100 ),
			'%' 
		) AS 差异 
	FROM
		(
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."新事业部" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源" 
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
		GROUP BY
			"数据源"."新事业部",
			"数据源"."新事业部" UNION ALL
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."商品区分" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源" 
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
		GROUP BY
			"数据源"."新事业部",
			"数据源"."商品区分" UNION ALL
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."渠道" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源" 
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
		GROUP BY
			"数据源"."新事业部",
			"数据源"."渠道" 
		) AS temp_tb 
	WHERE
		temp_tb."事业部" = '家庭投资部' 
ORDER BY
排序;
	
	
	
SELECT
	temp_tb."事业部",
	temp_tb."区分",
	(
	CASE
			
			WHEN temp_tb."区分" LIKE'%部' THEN
			1 
			WHEN temp_tb."区分" = 'TV商品' THEN
			2 
			WHEN temp_tb."区分" = 'IC商品' THEN
			3 
			WHEN temp_tb."区分" = 'TV' THEN
			4 
			WHEN temp_tb."区分" = '新媒体' THEN
			5 
			WHEN temp_tb."区分" = 'CTL' THEN
			6 
		END 
		) AS 排序
		,
		concat ( round(( temp_tb."去年销售金额" / temp_tb."去年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 去年转化率,
		concat ( round(( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 今年转化率,
		concat (
			round((( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) - ( temp_tb."去年销售金额" / temp_tb."去年订购金额" )) :: NUMERIC * 100 ),
			'%' 
		) AS 差异 
	FROM
		(
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."新事业部" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源" 
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
		GROUP BY
			"数据源"."新事业部",
			"数据源"."新事业部" UNION ALL
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."商品区分" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源" 
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
		GROUP BY
			"数据源"."新事业部",
			"数据源"."商品区分" UNION ALL
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."渠道" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源" 
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
		GROUP BY
			"数据源"."新事业部",
			"数据源"."渠道" 
		) AS temp_tb 
	WHERE
		temp_tb."事业部" = '电子电器部' 
ORDER BY
排序;
	
	
	
SELECT
	temp_tb."事业部",
	temp_tb."区分",
	(
	CASE
			
			WHEN temp_tb."区分" LIKE'%部' THEN
			1 
			WHEN temp_tb."区分" = 'TV商品' THEN
			2 
			WHEN temp_tb."区分" = 'IC商品' THEN
			3 
			WHEN temp_tb."区分" = 'TV' THEN
			4 
			WHEN temp_tb."区分" = '新媒体' THEN
			5 
			WHEN temp_tb."区分" = 'CTL' THEN
			6 
		END 
		) AS 排序
		,
		concat ( round(( temp_tb."去年销售金额" / temp_tb."去年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 去年转化率,
		concat ( round(( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 今年转化率,
		concat (
			round((( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) - ( temp_tb."去年销售金额" / temp_tb."去年订购金额" )) :: NUMERIC * 100 ),
			'%' 
		) AS 差异 
	FROM
		(
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."新事业部" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源" 
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
		GROUP BY
			"数据源"."新事业部",
			"数据源"."新事业部" UNION ALL
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."商品区分" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源" 
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
		GROUP BY
			"数据源"."新事业部",
			"数据源"."商品区分" UNION ALL
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."渠道" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源" 
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
		GROUP BY
			"数据源"."新事业部",
			"数据源"."渠道" 
		) AS temp_tb 
	WHERE
		temp_tb."事业部" = '家居家纺部' 
ORDER BY
排序;
	
	
	
SELECT
	temp_tb."事业部",
	temp_tb."区分",
	(
	CASE
			
			WHEN temp_tb."区分" LIKE'%部' THEN
			1 
			WHEN temp_tb."区分" = 'TV商品' THEN
			2 
			WHEN temp_tb."区分" = 'IC商品' THEN
			3 
			WHEN temp_tb."区分" = 'TV' THEN
			4 
			WHEN temp_tb."区分" = '新媒体' THEN
			5 
			WHEN temp_tb."区分" = 'CTL' THEN
			6 
		END 
		) AS 排序
		,
		concat ( round(( temp_tb."去年销售金额" / temp_tb."去年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 去年转化率,
		concat ( round(( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 今年转化率,
		concat (
			round((( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) - ( temp_tb."去年销售金额" / temp_tb."去年订购金额" )) :: NUMERIC * 100 ),
			'%' 
		) AS 差异 
	FROM
		(
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."新事业部" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源" 
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
		GROUP BY
			"数据源"."新事业部",
			"数据源"."新事业部" UNION ALL
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."商品区分" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源" 
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
		GROUP BY
			"数据源"."新事业部",
			"数据源"."商品区分" UNION ALL
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."渠道" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源"
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')	
		GROUP BY
			"数据源"."新事业部",
			"数据源"."渠道" 
		) AS temp_tb 
	WHERE
		temp_tb."事业部" = '家装家饰部' 
ORDER BY
排序;
	
	
	
SELECT
	temp_tb."事业部",
	temp_tb."区分",
	(
	CASE
			
			WHEN temp_tb."区分" LIKE'%部' THEN
			1 
			WHEN temp_tb."区分" = 'TV商品' THEN
			2 
			WHEN temp_tb."区分" = 'IC商品' THEN
			3 
			WHEN temp_tb."区分" = 'TV' THEN
			4 
			WHEN temp_tb."区分" = '新媒体' THEN
			5 
			WHEN temp_tb."区分" = 'CTL' THEN
			6 
		END 
		) AS 排序
		,
		concat ( round(( temp_tb."去年销售金额" / temp_tb."去年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 去年转化率,
		concat ( round(( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 今年转化率,
		concat (
			round((( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) - ( temp_tb."去年销售金额" / temp_tb."去年订购金额" )) :: NUMERIC * 100 ),
			'%' 
		) AS 差异 
	FROM
		(
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."新事业部" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源"
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')	
		GROUP BY
			"数据源"."新事业部",
			"数据源"."新事业部" UNION ALL
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."商品区分" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源"
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')	
		GROUP BY
			"数据源"."新事业部",
			"数据源"."商品区分" UNION ALL
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."渠道" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源"
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')	
		GROUP BY
			"数据源"."新事业部",
			"数据源"."渠道" 
		) AS temp_tb 
	WHERE
		temp_tb."事业部" = '美妆护理部' 
ORDER BY
排序;
	
	
	
SELECT
	temp_tb."事业部",
	temp_tb."区分",
	(
	CASE
			
			WHEN temp_tb."区分" LIKE'%部' THEN
			1 
			WHEN temp_tb."区分" = 'TV商品' THEN
			2 
			WHEN temp_tb."区分" = 'IC商品' THEN
			3 
			WHEN temp_tb."区分" = 'TV' THEN
			4 
			WHEN temp_tb."区分" = '新媒体' THEN
			5 
			WHEN temp_tb."区分" = 'CTL' THEN
			6 
		END 
		) AS 排序
		,
		concat ( round(( temp_tb."去年销售金额" / temp_tb."去年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 去年转化率,
		concat ( round(( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 今年转化率,
		concat (
			round((( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) - ( temp_tb."去年销售金额" / temp_tb."去年订购金额" )) :: NUMERIC * 100 ),
			'%' 
		) AS 差异 
	FROM
		(
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."新事业部" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源"
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')	
		GROUP BY
			"数据源"."新事业部",
			"数据源"."新事业部" UNION ALL
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."商品区分" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源"
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')	
		GROUP BY
			"数据源"."新事业部",
			"数据源"."商品区分" UNION ALL
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."渠道" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源"
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')	
		GROUP BY
			"数据源"."新事业部",
			"数据源"."渠道" 
		) AS temp_tb 
	WHERE
		temp_tb."事业部" = '生活日用品部' 
ORDER BY
排序;
	
	
	
SELECT
	temp_tb."事业部",
	temp_tb."区分",
	(
	CASE
			
			WHEN temp_tb."区分" LIKE'%部' THEN
			1 
			WHEN temp_tb."区分" = 'TV商品' THEN
			2 
			WHEN temp_tb."区分" = 'IC商品' THEN
			3 
			WHEN temp_tb."区分" = 'TV' THEN
			4 
			WHEN temp_tb."区分" = '新媒体' THEN
			5 
			WHEN temp_tb."区分" = 'CTL' THEN
			6 
		END 
		) AS 排序
		,
		concat ( round(( temp_tb."去年销售金额" / temp_tb."去年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 去年转化率,
		concat ( round(( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 今年转化率,
		concat (
			round((( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) - ( temp_tb."去年销售金额" / temp_tb."去年订购金额" )) :: NUMERIC * 100 ),
			'%' 
		) AS 差异 
	FROM
		(
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."新事业部" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源" 
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')
		GROUP BY
			"数据源"."新事业部",
			"数据源"."新事业部" UNION ALL
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."商品区分" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源"
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')	
		GROUP BY
			"数据源"."新事业部",
			"数据源"."商品区分" UNION ALL
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."渠道" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源"
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')	
		GROUP BY
			"数据源"."新事业部",
			"数据源"."渠道" 
		) AS temp_tb 
	WHERE
		temp_tb."事业部" = '艺术品交易部' 
ORDER BY
排序;
	
	
	
SELECT
	temp_tb."事业部",
	temp_tb."区分",
	(
	CASE
			
			WHEN temp_tb."区分" LIKE'%部' THEN
			1 
			WHEN temp_tb."区分" = 'TV商品' THEN
			2 
			WHEN temp_tb."区分" = 'IC商品' THEN
			3 
			WHEN temp_tb."区分" = 'TV' THEN
			4 
			WHEN temp_tb."区分" = '新媒体' THEN
			5 
			WHEN temp_tb."区分" = 'CTL' THEN
			6 
		END 
		) AS 排序
		,
		concat ( round(( temp_tb."去年销售金额" / temp_tb."去年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 去年转化率,
		concat ( round(( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) :: NUMERIC * 100 ), '%' ) AS 今年转化率,
		concat (
			round((( temp_tb."今年销售金额" / temp_tb."今年订购金额" ) - ( temp_tb."去年销售金额" / temp_tb."去年订购金额" )) :: NUMERIC * 100 ),
			'%' 
		) AS 差异 
	FROM
		(
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."新事业部" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源"
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')	
		GROUP BY
			"数据源"."新事业部",
			"数据源"."新事业部" UNION ALL
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."商品区分" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源"
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')	
		GROUP BY
			"数据源"."新事业部",
			"数据源"."商品区分" UNION ALL
		SELECT
			"数据源"."新事业部" AS 事业部,
			"数据源"."渠道" AS 区分,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."订购金额" ELSE NULL END ) AS 去年订购金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
			SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."订购金额" ELSE NULL END ) AS 今年订购金额 
		FROM
			"数据源"
		WHERE "数据源"."公司" IN ('电视购物公司','旅行社')	
		GROUP BY
			"数据源"."新事业部",
			"数据源"."渠道" 
		) AS temp_tb 
	WHERE
		temp_tb."事业部" = '珠宝饰品部' 
ORDER BY
排序;