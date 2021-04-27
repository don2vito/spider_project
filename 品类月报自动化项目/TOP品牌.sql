WITH a_tb AS (
SELECT
	"数据源"."新事业部",
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售金额" ELSE NULL END ) AS 去年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售金额" ELSE NULL END ) AS 今年销售金额,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售利润" ELSE NULL END ) AS 去年销售利润,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售利润" ELSE NULL END ) AS 今年销售利润,
	SUM ( CASE WHEN "数据源"."年份" = '2020' THEN "数据源"."销售数量" ELSE NULL END ) AS 去年销售数量,
	SUM ( CASE WHEN "数据源"."年份" = '2021' THEN "数据源"."销售数量" ELSE NULL END ) AS 今年销售数量 
FROM
	"数据源" 
WHERE "数据源"."公司" IN ( '电视购物公司', '旅行社' ) 
GROUP BY
	"数据源"."新事业部" 
	) ,
b_tb AS 
(SELECT
	"数据源"."新事业部",
	"数据源"."品牌编号",
	"数据源"."品牌名称",
	SUM ( "数据源"."销售金额" ) AS 销售金额
FROM
	"数据源"
WHERE
	"数据源"."新事业部" = '厨具厨电部'
	AND "数据源"."公司" IN ( '电视购物公司', '旅行社' ) 
	AND "数据源"."年份" = '2020' 
GROUP BY
	"数据源"."新事业部",
	"数据源"."品牌编号",
	"数据源"."品牌名称"
	ORDER BY SUM ( "数据源"."销售金额" ) DESC
	LIMIT 5),
	c_tb AS (
	SELECT
		b_tb."新事业部",
		b_tb."品牌编号",
		b_tb."品牌名称",
		b_tb."销售金额",
		concat ( ROUND( b_tb."销售金额" / a_tb."去年销售金额" :: NUMERIC * 100 ), '%' ) AS 销售金额占比 
	FROM
		a_tb
		LEFT JOIN b_tb ON a_tb."新事业部" = b_tb."新事业部"
	WHERE
		a_tb."新事业部" = '厨具厨电部' 
	),
	d_tb AS
( SELECT
c_tb."新事业部" AS 事业部,
ROW_NUMBER() OVER() AS 行数,
( c_tb."品牌名称" || chr(10) || c_tb."销售金额" :: TEXT || chr(10) || c_tb."销售金额占比" ) AS 去年销售金额_TOP_5_品牌 
FROM
	c_tb
	),
	e_tb AS 
(SELECT
	"数据源"."新事业部",
	"数据源"."品牌编号",
	"数据源"."品牌名称",
	SUM ( "数据源"."销售金额" ) AS 销售金额
FROM
	"数据源"
WHERE
	"数据源"."新事业部" = '厨具厨电部'
	AND "数据源"."公司" IN ( '电视购物公司', '旅行社' ) 
	AND "数据源"."年份" = '2021' 
GROUP BY
	"数据源"."新事业部",
	"数据源"."品牌编号",
	"数据源"."品牌名称"
	ORDER BY SUM ( "数据源"."销售金额" ) DESC
	LIMIT 5),
	f_tb AS
	(SELECT
		e_tb."新事业部",
		e_tb."品牌编号",
		e_tb."品牌名称",
		e_tb."销售金额",
		concat ( ROUND( e_tb."销售金额" / a_tb."今年销售金额" :: NUMERIC * 100 ), '%' ) AS 销售金额占比 
	FROM
		a_tb
		LEFT JOIN e_tb ON a_tb."新事业部" = e_tb."新事业部" 
	WHERE
		a_tb."新事业部" = '厨具厨电部' 
	),
	g_tb AS
( SELECT
f_tb."新事业部" AS 事业部,
ROW_NUMBER() OVER() AS 行数,
( f_tb."品牌名称" || chr(10) || f_tb."销售金额" :: TEXT || chr(10) || f_tb."销售金额占比" ) AS 今年销售金额_TOP_5_品牌 
FROM
	f_tb
	),
	h_tb AS 
(SELECT
	"数据源"."新事业部",
	"数据源"."品牌编号",
	"数据源"."品牌名称",
	SUM ( "数据源"."销售利润" ) AS 销售利润
FROM
	"数据源"
WHERE
	"数据源"."新事业部" = '厨具厨电部'
	AND "数据源"."公司" IN ( '电视购物公司', '旅行社' ) 
	AND "数据源"."年份" = '2020' 
GROUP BY
	"数据源"."新事业部",
	"数据源"."品牌编号",
	"数据源"."品牌名称"
	ORDER BY SUM ( "数据源"."销售利润" ) DESC
	LIMIT 5),
	i_tb AS
	(SELECT
		h_tb."新事业部",
		h_tb."品牌编号",
		h_tb."品牌名称",
		h_tb."销售利润",
		concat ( ROUND( h_tb."销售利润" / a_tb."去年销售利润" :: NUMERIC * 100 ), '%' ) AS 销售利润占比 
	FROM
		a_tb
		LEFT JOIN h_tb ON a_tb."新事业部" = h_tb."新事业部"
	WHERE
		a_tb."新事业部" = '厨具厨电部' 
	),
	j_tb AS
( SELECT
i_tb."新事业部" AS 事业部,
ROW_NUMBER() OVER() AS 行数,
( i_tb."品牌名称" || chr(10) || i_tb."销售利润" :: TEXT || chr(10) || i_tb."销售利润占比" ) AS 去年销售利润_TOP_5_品牌 
FROM
	i_tb
	),
k_tb AS 
(SELECT
	"数据源"."新事业部",
	"数据源"."品牌编号",
	"数据源"."品牌名称",
	SUM ( "数据源"."销售利润" ) AS 销售利润
FROM
	"数据源"
WHERE
	"数据源"."新事业部" = '厨具厨电部'
	AND "数据源"."公司" IN ( '电视购物公司', '旅行社' ) 
	AND "数据源"."年份" = '2021' 
GROUP BY
	"数据源"."新事业部",
	"数据源"."品牌编号",
	"数据源"."品牌名称"
	ORDER BY SUM ( "数据源"."销售利润" ) DESC
	LIMIT 5),
	l_tb AS
	(SELECT
		k_tb."新事业部",
		k_tb."品牌编号",
		k_tb."品牌名称",
		k_tb."销售利润",
		concat ( ROUND( k_tb."销售利润" / a_tb."今年销售利润" :: NUMERIC * 100 ), '%' ) AS 销售利润占比 
	FROM
		a_tb
		LEFT JOIN k_tb ON a_tb."新事业部" = k_tb."新事业部"
	WHERE
		a_tb."新事业部" = '厨具厨电部' 
	),
	m_tb AS
( SELECT
l_tb."新事业部" AS 事业部,
ROW_NUMBER()  OVER() AS 行数,
( l_tb."品牌名称" || chr(10) || l_tb."销售利润" :: TEXT || chr(10) || l_tb."销售利润占比" ) AS 今年销售利润_TOP_5_品牌 
FROM
	l_tb
	),
n_tb AS 
(SELECT
	"数据源"."新事业部",
	"数据源"."品牌编号",
	"数据源"."品牌名称",
	SUM ( "数据源"."销售数量" ) AS 销售数量
FROM
	"数据源"
WHERE
	"数据源"."新事业部" = '厨具厨电部'
	AND "数据源"."公司" IN ( '电视购物公司', '旅行社' ) 
	AND "数据源"."年份" = '2020' 
GROUP BY
	"数据源"."新事业部",
	"数据源"."品牌编号",
	"数据源"."品牌名称"
	ORDER BY SUM ( "数据源"."销售数量" ) DESC
	LIMIT 5),
	o_tb AS
	(SELECT
		n_tb."新事业部",
		n_tb."品牌编号",
		n_tb."品牌名称",
		n_tb."销售数量",
		concat ( ROUND( n_tb."销售数量" / a_tb."去年销售数量" :: NUMERIC * 100 ), '%' ) AS 销售数量占比 
	FROM
		a_tb
		LEFT JOIN n_tb ON a_tb."新事业部" = n_tb."新事业部"
	WHERE
		a_tb."新事业部" = '厨具厨电部' 
	),
	p_tb AS
( SELECT
o_tb."新事业部" AS 事业部,
ROW_NUMBER()  OVER() AS 行数,
( o_tb."品牌名称" || chr(10) || o_tb."销售数量" :: TEXT || chr(10) || o_tb."销售数量占比" ) AS 去年销售数量_TOP_5_品牌 
FROM
	o_tb
	),
q_tb AS 
(SELECT
	"数据源"."新事业部",
	"数据源"."品牌编号",
	"数据源"."品牌名称",
	SUM ( "数据源"."销售数量" ) AS 销售数量
FROM
	"数据源"
WHERE
	"数据源"."新事业部" = '厨具厨电部'
	AND "数据源"."公司" IN ( '电视购物公司', '旅行社' ) 
	AND "数据源"."年份" = '2021' 
GROUP BY
	"数据源"."新事业部",
	"数据源"."品牌编号",
	"数据源"."品牌名称"
	ORDER BY SUM ( "数据源"."销售数量" ) DESC
	LIMIT 5),
	r_tb AS
	(SELECT
		q_tb."新事业部",
		q_tb."品牌编号",
		q_tb."品牌名称",
		q_tb."销售数量",
		concat ( ROUND( q_tb."销售数量" / a_tb."今年销售数量" :: NUMERIC * 100 ), '%' ) AS 销售数量占比 
	FROM
		a_tb
		LEFT JOIN q_tb ON a_tb."新事业部" = q_tb."新事业部"
	WHERE
		a_tb."新事业部" = '厨具厨电部' 
	),
	s_tb AS
( SELECT
r_tb."新事业部" AS 事业部,
ROW_NUMBER()  OVER() AS 行数,
( r_tb."品牌名称" || chr(10) || r_tb."销售数量" :: TEXT || chr(10) || r_tb."销售数量占比" ) AS 今年销售数量_TOP_5_品牌 
FROM
	r_tb
	)	
	
	SELECT d_tb.*,g_tb.今年销售金额_TOP_5_品牌,j_tb.去年销售利润_TOP_5_品牌,m_tb.今年销售利润_TOP_5_品牌,p_tb.去年销售数量_TOP_5_品牌,s_tb.今年销售数量_TOP_5_品牌
	FROM d_tb
	INNER JOIN g_tb ON d_tb."行数" = g_tb."行数"
	INNER JOIN j_tb ON d_tb."行数" = j_tb."行数"
	INNER JOIN m_tb ON d_tb."行数" = m_tb."行数"
	INNER JOIN p_tb ON d_tb."行数" = p_tb."行数"
	INNER JOIN s_tb ON d_tb."行数" = s_tb."行数";