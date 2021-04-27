WITH a_tb AS (
SELECT
	"����Դ"."����ҵ��",
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."��������" ELSE NULL END ) AS ȥ����������,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."��������" ELSE NULL END ) AS ������������,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."��������" ELSE NULL END ) AS ȥ����������,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."��������" ELSE NULL END ) AS ������������ 
FROM
	"����Դ" 
WHERE "����Դ"."��˾" IN ( '���ӹ��﹫˾', '������' ) 
GROUP BY
	"����Դ"."����ҵ��" 
	) ,
b_tb AS 
(SELECT
	"����Դ"."����ҵ��",
	"����Դ"."Ʒ�Ʊ��",
	"����Դ"."Ʒ������",
	SUM ( "����Դ"."���۽��" ) AS ���۽��
FROM
	"����Դ"
WHERE
	"����Դ"."����ҵ��" = '���߳��粿'
	AND "����Դ"."��˾" IN ( '���ӹ��﹫˾', '������' ) 
	AND "����Դ"."���" = '2020' 
GROUP BY
	"����Դ"."����ҵ��",
	"����Դ"."Ʒ�Ʊ��",
	"����Դ"."Ʒ������"
	ORDER BY SUM ( "����Դ"."���۽��" ) DESC
	LIMIT 5),
	c_tb AS (
	SELECT
		b_tb."����ҵ��",
		b_tb."Ʒ�Ʊ��",
		b_tb."Ʒ������",
		b_tb."���۽��",
		concat ( ROUND( b_tb."���۽��" / a_tb."ȥ�����۽��" :: NUMERIC * 100 ), '%' ) AS ���۽��ռ�� 
	FROM
		a_tb
		LEFT JOIN b_tb ON a_tb."����ҵ��" = b_tb."����ҵ��"
	WHERE
		a_tb."����ҵ��" = '���߳��粿' 
	),
	d_tb AS
( SELECT
c_tb."����ҵ��" AS ��ҵ��,
ROW_NUMBER() OVER() AS ����,
( c_tb."Ʒ������" || chr(10) || c_tb."���۽��" :: TEXT || chr(10) || c_tb."���۽��ռ��" ) AS ȥ�����۽��_TOP_5_Ʒ�� 
FROM
	c_tb
	),
	e_tb AS 
(SELECT
	"����Դ"."����ҵ��",
	"����Դ"."Ʒ�Ʊ��",
	"����Դ"."Ʒ������",
	SUM ( "����Դ"."���۽��" ) AS ���۽��
FROM
	"����Դ"
WHERE
	"����Դ"."����ҵ��" = '���߳��粿'
	AND "����Դ"."��˾" IN ( '���ӹ��﹫˾', '������' ) 
	AND "����Դ"."���" = '2021' 
GROUP BY
	"����Դ"."����ҵ��",
	"����Դ"."Ʒ�Ʊ��",
	"����Դ"."Ʒ������"
	ORDER BY SUM ( "����Դ"."���۽��" ) DESC
	LIMIT 5),
	f_tb AS
	(SELECT
		e_tb."����ҵ��",
		e_tb."Ʒ�Ʊ��",
		e_tb."Ʒ������",
		e_tb."���۽��",
		concat ( ROUND( e_tb."���۽��" / a_tb."�������۽��" :: NUMERIC * 100 ), '%' ) AS ���۽��ռ�� 
	FROM
		a_tb
		LEFT JOIN e_tb ON a_tb."����ҵ��" = e_tb."����ҵ��" 
	WHERE
		a_tb."����ҵ��" = '���߳��粿' 
	),
	g_tb AS
( SELECT
f_tb."����ҵ��" AS ��ҵ��,
ROW_NUMBER() OVER() AS ����,
( f_tb."Ʒ������" || chr(10) || f_tb."���۽��" :: TEXT || chr(10) || f_tb."���۽��ռ��" ) AS �������۽��_TOP_5_Ʒ�� 
FROM
	f_tb
	),
	h_tb AS 
(SELECT
	"����Դ"."����ҵ��",
	"����Դ"."Ʒ�Ʊ��",
	"����Դ"."Ʒ������",
	SUM ( "����Դ"."��������" ) AS ��������
FROM
	"����Դ"
WHERE
	"����Դ"."����ҵ��" = '���߳��粿'
	AND "����Դ"."��˾" IN ( '���ӹ��﹫˾', '������' ) 
	AND "����Դ"."���" = '2020' 
GROUP BY
	"����Դ"."����ҵ��",
	"����Դ"."Ʒ�Ʊ��",
	"����Դ"."Ʒ������"
	ORDER BY SUM ( "����Դ"."��������" ) DESC
	LIMIT 5),
	i_tb AS
	(SELECT
		h_tb."����ҵ��",
		h_tb."Ʒ�Ʊ��",
		h_tb."Ʒ������",
		h_tb."��������",
		concat ( ROUND( h_tb."��������" / a_tb."ȥ����������" :: NUMERIC * 100 ), '%' ) AS ��������ռ�� 
	FROM
		a_tb
		LEFT JOIN h_tb ON a_tb."����ҵ��" = h_tb."����ҵ��"
	WHERE
		a_tb."����ҵ��" = '���߳��粿' 
	),
	j_tb AS
( SELECT
i_tb."����ҵ��" AS ��ҵ��,
ROW_NUMBER() OVER() AS ����,
( i_tb."Ʒ������" || chr(10) || i_tb."��������" :: TEXT || chr(10) || i_tb."��������ռ��" ) AS ȥ����������_TOP_5_Ʒ�� 
FROM
	i_tb
	),
k_tb AS 
(SELECT
	"����Դ"."����ҵ��",
	"����Դ"."Ʒ�Ʊ��",
	"����Դ"."Ʒ������",
	SUM ( "����Դ"."��������" ) AS ��������
FROM
	"����Դ"
WHERE
	"����Դ"."����ҵ��" = '���߳��粿'
	AND "����Դ"."��˾" IN ( '���ӹ��﹫˾', '������' ) 
	AND "����Դ"."���" = '2021' 
GROUP BY
	"����Դ"."����ҵ��",
	"����Դ"."Ʒ�Ʊ��",
	"����Դ"."Ʒ������"
	ORDER BY SUM ( "����Դ"."��������" ) DESC
	LIMIT 5),
	l_tb AS
	(SELECT
		k_tb."����ҵ��",
		k_tb."Ʒ�Ʊ��",
		k_tb."Ʒ������",
		k_tb."��������",
		concat ( ROUND( k_tb."��������" / a_tb."������������" :: NUMERIC * 100 ), '%' ) AS ��������ռ�� 
	FROM
		a_tb
		LEFT JOIN k_tb ON a_tb."����ҵ��" = k_tb."����ҵ��"
	WHERE
		a_tb."����ҵ��" = '���߳��粿' 
	),
	m_tb AS
( SELECT
l_tb."����ҵ��" AS ��ҵ��,
ROW_NUMBER()  OVER() AS ����,
( l_tb."Ʒ������" || chr(10) || l_tb."��������" :: TEXT || chr(10) || l_tb."��������ռ��" ) AS ������������_TOP_5_Ʒ�� 
FROM
	l_tb
	),
n_tb AS 
(SELECT
	"����Դ"."����ҵ��",
	"����Դ"."Ʒ�Ʊ��",
	"����Դ"."Ʒ������",
	SUM ( "����Դ"."��������" ) AS ��������
FROM
	"����Դ"
WHERE
	"����Դ"."����ҵ��" = '���߳��粿'
	AND "����Դ"."��˾" IN ( '���ӹ��﹫˾', '������' ) 
	AND "����Դ"."���" = '2020' 
GROUP BY
	"����Դ"."����ҵ��",
	"����Դ"."Ʒ�Ʊ��",
	"����Դ"."Ʒ������"
	ORDER BY SUM ( "����Դ"."��������" ) DESC
	LIMIT 5),
	o_tb AS
	(SELECT
		n_tb."����ҵ��",
		n_tb."Ʒ�Ʊ��",
		n_tb."Ʒ������",
		n_tb."��������",
		concat ( ROUND( n_tb."��������" / a_tb."ȥ����������" :: NUMERIC * 100 ), '%' ) AS ��������ռ�� 
	FROM
		a_tb
		LEFT JOIN n_tb ON a_tb."����ҵ��" = n_tb."����ҵ��"
	WHERE
		a_tb."����ҵ��" = '���߳��粿' 
	),
	p_tb AS
( SELECT
o_tb."����ҵ��" AS ��ҵ��,
ROW_NUMBER()  OVER() AS ����,
( o_tb."Ʒ������" || chr(10) || o_tb."��������" :: TEXT || chr(10) || o_tb."��������ռ��" ) AS ȥ����������_TOP_5_Ʒ�� 
FROM
	o_tb
	),
q_tb AS 
(SELECT
	"����Դ"."����ҵ��",
	"����Դ"."Ʒ�Ʊ��",
	"����Դ"."Ʒ������",
	SUM ( "����Դ"."��������" ) AS ��������
FROM
	"����Դ"
WHERE
	"����Դ"."����ҵ��" = '���߳��粿'
	AND "����Դ"."��˾" IN ( '���ӹ��﹫˾', '������' ) 
	AND "����Դ"."���" = '2021' 
GROUP BY
	"����Դ"."����ҵ��",
	"����Դ"."Ʒ�Ʊ��",
	"����Դ"."Ʒ������"
	ORDER BY SUM ( "����Դ"."��������" ) DESC
	LIMIT 5),
	r_tb AS
	(SELECT
		q_tb."����ҵ��",
		q_tb."Ʒ�Ʊ��",
		q_tb."Ʒ������",
		q_tb."��������",
		concat ( ROUND( q_tb."��������" / a_tb."������������" :: NUMERIC * 100 ), '%' ) AS ��������ռ�� 
	FROM
		a_tb
		LEFT JOIN q_tb ON a_tb."����ҵ��" = q_tb."����ҵ��"
	WHERE
		a_tb."����ҵ��" = '���߳��粿' 
	),
	s_tb AS
( SELECT
r_tb."����ҵ��" AS ��ҵ��,
ROW_NUMBER()  OVER() AS ����,
( r_tb."Ʒ������" || chr(10) || r_tb."��������" :: TEXT || chr(10) || r_tb."��������ռ��" ) AS ������������_TOP_5_Ʒ�� 
FROM
	r_tb
	)	
	
	SELECT d_tb.*,g_tb.�������۽��_TOP_5_Ʒ��,j_tb.ȥ����������_TOP_5_Ʒ��,m_tb.������������_TOP_5_Ʒ��,p_tb.ȥ����������_TOP_5_Ʒ��,s_tb.������������_TOP_5_Ʒ��
	FROM d_tb
	INNER JOIN g_tb ON d_tb."����" = g_tb."����"
	INNER JOIN j_tb ON d_tb."����" = j_tb."����"
	INNER JOIN m_tb ON d_tb."����" = m_tb."����"
	INNER JOIN p_tb ON d_tb."����" = p_tb."����"
	INNER JOIN s_tb ON d_tb."����" = s_tb."����";