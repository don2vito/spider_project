SELECT
	temp_tb."��ҵ��",
	temp_tb."����",
	(
CASE
	
	WHEN temp_tb."����" LIKE'%��' THEN
	1 
	WHEN temp_tb."����" = 'TV��Ʒ' THEN
	2 
	WHEN temp_tb."����" = 'IC��Ʒ' THEN
	3 
	WHEN temp_tb."����" = 'TV' THEN
	4 
	WHEN temp_tb."����" = '��ý��' THEN
	5 
	WHEN temp_tb."����" = 'CTL' THEN
	6 
END 
	) AS ����
	,
	concat ( round(( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" ) :: NUMERIC * 100 ), '%' ) AS ȥ��ת����,
	concat ( round(( temp_tb."�������۽��" / temp_tb."���궩�����" ) :: NUMERIC * 100 ), '%' ) AS ����ת����,
	concat (
		round((( temp_tb."�������۽��" / temp_tb."���궩�����" ) - ( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" )) :: NUMERIC * 100 ),
		'%' 
	) AS ���� 
FROM
	(
	SELECT
		"����Դ"."����ҵ��" AS ��ҵ��,
		"����Դ"."����ҵ��" AS ����,
		SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
		SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
		SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
		SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
	FROM
		"����Դ" 
	WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
	GROUP BY
		"����Դ"."����ҵ��",
		"����Դ"."����ҵ��" UNION ALL
	SELECT
		"����Դ"."����ҵ��" AS ��ҵ��,
		"����Դ"."��Ʒ����" AS ����,
		SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
		SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
		SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
		SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
	FROM
		"����Դ" 
	WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
	GROUP BY
		"����Դ"."����ҵ��",
		"����Դ"."��Ʒ����" UNION ALL
	SELECT
		"����Դ"."����ҵ��" AS ��ҵ��,
		"����Դ"."����" AS ����,
		SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
		SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
		SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
		SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
	FROM
		"����Դ" 
	WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
	GROUP BY
		"����Դ"."����ҵ��",
		"����Դ"."����" 
	) AS temp_tb 
WHERE
	temp_tb."��ҵ��" = '���߳��粿' 
ORDER BY
	����;
	
	
	
SELECT
	temp_tb."��ҵ��",
	temp_tb."����",
	(
	CASE
			
			WHEN temp_tb."����" LIKE'%��' THEN
			1 
			WHEN temp_tb."����" = 'TV��Ʒ' THEN
			2 
			WHEN temp_tb."����" = 'IC��Ʒ' THEN
			3 
			WHEN temp_tb."����" = 'TV' THEN
			4 
			WHEN temp_tb."����" = '��ý��' THEN
			5 
			WHEN temp_tb."����" = 'CTL' THEN
			6 
		END 
		) AS ����
		,
		concat ( round(( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" ) :: NUMERIC * 100 ), '%' ) AS ȥ��ת����,
		concat ( round(( temp_tb."�������۽��" / temp_tb."���궩�����" ) :: NUMERIC * 100 ), '%' ) AS ����ת����,
		concat (
			round((( temp_tb."�������۽��" / temp_tb."���궩�����" ) - ( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" )) :: NUMERIC * 100 ),
			'%' 
		) AS ���� 
	FROM
		(
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."����ҵ��" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ" 
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."����ҵ��" UNION ALL
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."��Ʒ����" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ" 
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."��Ʒ����" UNION ALL
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."����" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ" 
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."����" 
		) AS temp_tb 
	WHERE
		temp_tb."��ҵ��" = '��ͥͶ�ʲ�' 
ORDER BY
����;
	
	
	
SELECT
	temp_tb."��ҵ��",
	temp_tb."����",
	(
	CASE
			
			WHEN temp_tb."����" LIKE'%��' THEN
			1 
			WHEN temp_tb."����" = 'TV��Ʒ' THEN
			2 
			WHEN temp_tb."����" = 'IC��Ʒ' THEN
			3 
			WHEN temp_tb."����" = 'TV' THEN
			4 
			WHEN temp_tb."����" = '��ý��' THEN
			5 
			WHEN temp_tb."����" = 'CTL' THEN
			6 
		END 
		) AS ����
		,
		concat ( round(( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" ) :: NUMERIC * 100 ), '%' ) AS ȥ��ת����,
		concat ( round(( temp_tb."�������۽��" / temp_tb."���궩�����" ) :: NUMERIC * 100 ), '%' ) AS ����ת����,
		concat (
			round((( temp_tb."�������۽��" / temp_tb."���궩�����" ) - ( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" )) :: NUMERIC * 100 ),
			'%' 
		) AS ���� 
	FROM
		(
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."����ҵ��" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ" 
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."����ҵ��" UNION ALL
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."��Ʒ����" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ" 
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."��Ʒ����" UNION ALL
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."����" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ" 
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."����" 
		) AS temp_tb 
	WHERE
		temp_tb."��ҵ��" = '����������' 
ORDER BY
����;
	
	
	
SELECT
	temp_tb."��ҵ��",
	temp_tb."����",
	(
	CASE
			
			WHEN temp_tb."����" LIKE'%��' THEN
			1 
			WHEN temp_tb."����" = 'TV��Ʒ' THEN
			2 
			WHEN temp_tb."����" = 'IC��Ʒ' THEN
			3 
			WHEN temp_tb."����" = 'TV' THEN
			4 
			WHEN temp_tb."����" = '��ý��' THEN
			5 
			WHEN temp_tb."����" = 'CTL' THEN
			6 
		END 
		) AS ����
		,
		concat ( round(( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" ) :: NUMERIC * 100 ), '%' ) AS ȥ��ת����,
		concat ( round(( temp_tb."�������۽��" / temp_tb."���궩�����" ) :: NUMERIC * 100 ), '%' ) AS ����ת����,
		concat (
			round((( temp_tb."�������۽��" / temp_tb."���궩�����" ) - ( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" )) :: NUMERIC * 100 ),
			'%' 
		) AS ���� 
	FROM
		(
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."����ҵ��" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ"
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')	
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."����ҵ��" UNION ALL
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."��Ʒ����" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ" 
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."��Ʒ����" UNION ALL
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."����" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ" 
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."����" 
		) AS temp_tb 
	WHERE
		temp_tb."��ҵ��" = '���з��β�' 
ORDER BY
����;
	
	
	
SELECT
	temp_tb."��ҵ��",
	temp_tb."����",
	(
	CASE
			
			WHEN temp_tb."����" LIKE'%��' THEN
			1 
			WHEN temp_tb."����" = 'TV��Ʒ' THEN
			2 
			WHEN temp_tb."����" = 'IC��Ʒ' THEN
			3 
			WHEN temp_tb."����" = 'TV' THEN
			4 
			WHEN temp_tb."����" = '��ý��' THEN
			5 
			WHEN temp_tb."����" = 'CTL' THEN
			6 
		END 
		) AS ����
		,
		concat ( round(( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" ) :: NUMERIC * 100 ), '%' ) AS ȥ��ת����,
		concat ( round(( temp_tb."�������۽��" / temp_tb."���궩�����" ) :: NUMERIC * 100 ), '%' ) AS ����ת����,
		concat (
			round((( temp_tb."�������۽��" / temp_tb."���궩�����" ) - ( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" )) :: NUMERIC * 100 ),
			'%' 
		) AS ���� 
	FROM
		(
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."����ҵ��" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ" 
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."����ҵ��" UNION ALL
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."��Ʒ����" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ" 
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."��Ʒ����" UNION ALL
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."����" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ" 
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."����" 
		) AS temp_tb 
	WHERE
		temp_tb."��ҵ��" = '������ʳ��' 
ORDER BY
����;
	
	
	
SELECT
	temp_tb."��ҵ��",
	temp_tb."����",
	(
	CASE
			
			WHEN temp_tb."����" LIKE'%��' THEN
			1 
			WHEN temp_tb."����" = 'TV��Ʒ' THEN
			2 
			WHEN temp_tb."����" = 'IC��Ʒ' THEN
			3 
			WHEN temp_tb."����" = 'TV' THEN
			4 
			WHEN temp_tb."����" = '��ý��' THEN
			5 
			WHEN temp_tb."����" = 'CTL' THEN
			6 
		END 
		) AS ����
		,
		concat ( round(( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" ) :: NUMERIC * 100 ), '%' ) AS ȥ��ת����,
		concat ( round(( temp_tb."�������۽��" / temp_tb."���궩�����" ) :: NUMERIC * 100 ), '%' ) AS ����ת����,
		concat (
			round((( temp_tb."�������۽��" / temp_tb."���궩�����" ) - ( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" )) :: NUMERIC * 100 ),
			'%' 
		) AS ���� 
	FROM
		(
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."����ҵ��" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ" 
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."����ҵ��" UNION ALL
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."��Ʒ����" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ" 
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."��Ʒ����" UNION ALL
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."����" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ"
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')	
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."����" 
		) AS temp_tb 
	WHERE
		temp_tb."��ҵ��" = '������β�' 
ORDER BY
����;
	
	
	
SELECT
	temp_tb."��ҵ��",
	temp_tb."����",
	(
	CASE
			
			WHEN temp_tb."����" LIKE'%��' THEN
			1 
			WHEN temp_tb."����" = 'TV��Ʒ' THEN
			2 
			WHEN temp_tb."����" = 'IC��Ʒ' THEN
			3 
			WHEN temp_tb."����" = 'TV' THEN
			4 
			WHEN temp_tb."����" = '��ý��' THEN
			5 
			WHEN temp_tb."����" = 'CTL' THEN
			6 
		END 
		) AS ����
		,
		concat ( round(( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" ) :: NUMERIC * 100 ), '%' ) AS ȥ��ת����,
		concat ( round(( temp_tb."�������۽��" / temp_tb."���궩�����" ) :: NUMERIC * 100 ), '%' ) AS ����ת����,
		concat (
			round((( temp_tb."�������۽��" / temp_tb."���궩�����" ) - ( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" )) :: NUMERIC * 100 ),
			'%' 
		) AS ���� 
	FROM
		(
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."����ҵ��" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ" 
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."����ҵ��" UNION ALL
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."��Ʒ����" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ" 
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."��Ʒ����" UNION ALL
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."����" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ"
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')	
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."����" 
		) AS temp_tb 
	WHERE
		temp_tb."��ҵ��" = '���ѷ���' 
ORDER BY
����;
	
	
	
SELECT
	temp_tb."��ҵ��",
	temp_tb."����",
	(
	CASE
			
			WHEN temp_tb."����" LIKE'%��' THEN
			1 
			WHEN temp_tb."����" = 'TV��Ʒ' THEN
			2 
			WHEN temp_tb."����" = 'IC��Ʒ' THEN
			3 
			WHEN temp_tb."����" = 'TV' THEN
			4 
			WHEN temp_tb."����" = '��ý��' THEN
			5 
			WHEN temp_tb."����" = 'CTL' THEN
			6 
		END 
		) AS ����
		,
		concat ( round(( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" ) :: NUMERIC * 100 ), '%' ) AS ȥ��ת����,
		concat ( round(( temp_tb."�������۽��" / temp_tb."���궩�����" ) :: NUMERIC * 100 ), '%' ) AS ����ת����,
		concat (
			round((( temp_tb."�������۽��" / temp_tb."���궩�����" ) - ( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" )) :: NUMERIC * 100 ),
			'%' 
		) AS ���� 
	FROM
		(
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."����ҵ��" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ" 
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."����ҵ��" UNION ALL
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."��Ʒ����" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ" 
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."��Ʒ����" UNION ALL
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."����" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ" 
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."����" 
		) AS temp_tb 
	WHERE
		temp_tb."��ҵ��" = '��ͥͶ�ʲ�' 
ORDER BY
����;
	
	
	
SELECT
	temp_tb."��ҵ��",
	temp_tb."����",
	(
	CASE
			
			WHEN temp_tb."����" LIKE'%��' THEN
			1 
			WHEN temp_tb."����" = 'TV��Ʒ' THEN
			2 
			WHEN temp_tb."����" = 'IC��Ʒ' THEN
			3 
			WHEN temp_tb."����" = 'TV' THEN
			4 
			WHEN temp_tb."����" = '��ý��' THEN
			5 
			WHEN temp_tb."����" = 'CTL' THEN
			6 
		END 
		) AS ����
		,
		concat ( round(( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" ) :: NUMERIC * 100 ), '%' ) AS ȥ��ת����,
		concat ( round(( temp_tb."�������۽��" / temp_tb."���궩�����" ) :: NUMERIC * 100 ), '%' ) AS ����ת����,
		concat (
			round((( temp_tb."�������۽��" / temp_tb."���궩�����" ) - ( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" )) :: NUMERIC * 100 ),
			'%' 
		) AS ���� 
	FROM
		(
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."����ҵ��" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ" 
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."����ҵ��" UNION ALL
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."��Ʒ����" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ" 
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."��Ʒ����" UNION ALL
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."����" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ" 
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."����" 
		) AS temp_tb 
	WHERE
		temp_tb."��ҵ��" = '���ӵ�����' 
ORDER BY
����;
	
	
	
SELECT
	temp_tb."��ҵ��",
	temp_tb."����",
	(
	CASE
			
			WHEN temp_tb."����" LIKE'%��' THEN
			1 
			WHEN temp_tb."����" = 'TV��Ʒ' THEN
			2 
			WHEN temp_tb."����" = 'IC��Ʒ' THEN
			3 
			WHEN temp_tb."����" = 'TV' THEN
			4 
			WHEN temp_tb."����" = '��ý��' THEN
			5 
			WHEN temp_tb."����" = 'CTL' THEN
			6 
		END 
		) AS ����
		,
		concat ( round(( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" ) :: NUMERIC * 100 ), '%' ) AS ȥ��ת����,
		concat ( round(( temp_tb."�������۽��" / temp_tb."���궩�����" ) :: NUMERIC * 100 ), '%' ) AS ����ת����,
		concat (
			round((( temp_tb."�������۽��" / temp_tb."���궩�����" ) - ( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" )) :: NUMERIC * 100 ),
			'%' 
		) AS ���� 
	FROM
		(
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."����ҵ��" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ" 
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."����ҵ��" UNION ALL
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."��Ʒ����" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ" 
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."��Ʒ����" UNION ALL
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."����" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ" 
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."����" 
		) AS temp_tb 
	WHERE
		temp_tb."��ҵ��" = '�ҾӼҷĲ�' 
ORDER BY
����;
	
	
	
SELECT
	temp_tb."��ҵ��",
	temp_tb."����",
	(
	CASE
			
			WHEN temp_tb."����" LIKE'%��' THEN
			1 
			WHEN temp_tb."����" = 'TV��Ʒ' THEN
			2 
			WHEN temp_tb."����" = 'IC��Ʒ' THEN
			3 
			WHEN temp_tb."����" = 'TV' THEN
			4 
			WHEN temp_tb."����" = '��ý��' THEN
			5 
			WHEN temp_tb."����" = 'CTL' THEN
			6 
		END 
		) AS ����
		,
		concat ( round(( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" ) :: NUMERIC * 100 ), '%' ) AS ȥ��ת����,
		concat ( round(( temp_tb."�������۽��" / temp_tb."���궩�����" ) :: NUMERIC * 100 ), '%' ) AS ����ת����,
		concat (
			round((( temp_tb."�������۽��" / temp_tb."���궩�����" ) - ( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" )) :: NUMERIC * 100 ),
			'%' 
		) AS ���� 
	FROM
		(
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."����ҵ��" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ" 
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."����ҵ��" UNION ALL
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."��Ʒ����" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ" 
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."��Ʒ����" UNION ALL
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."����" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ"
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')	
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."����" 
		) AS temp_tb 
	WHERE
		temp_tb."��ҵ��" = '��װ���β�' 
ORDER BY
����;
	
	
	
SELECT
	temp_tb."��ҵ��",
	temp_tb."����",
	(
	CASE
			
			WHEN temp_tb."����" LIKE'%��' THEN
			1 
			WHEN temp_tb."����" = 'TV��Ʒ' THEN
			2 
			WHEN temp_tb."����" = 'IC��Ʒ' THEN
			3 
			WHEN temp_tb."����" = 'TV' THEN
			4 
			WHEN temp_tb."����" = '��ý��' THEN
			5 
			WHEN temp_tb."����" = 'CTL' THEN
			6 
		END 
		) AS ����
		,
		concat ( round(( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" ) :: NUMERIC * 100 ), '%' ) AS ȥ��ת����,
		concat ( round(( temp_tb."�������۽��" / temp_tb."���궩�����" ) :: NUMERIC * 100 ), '%' ) AS ����ת����,
		concat (
			round((( temp_tb."�������۽��" / temp_tb."���궩�����" ) - ( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" )) :: NUMERIC * 100 ),
			'%' 
		) AS ���� 
	FROM
		(
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."����ҵ��" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ"
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')	
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."����ҵ��" UNION ALL
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."��Ʒ����" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ"
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')	
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."��Ʒ����" UNION ALL
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."����" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ"
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')	
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."����" 
		) AS temp_tb 
	WHERE
		temp_tb."��ҵ��" = '��ױ����' 
ORDER BY
����;
	
	
	
SELECT
	temp_tb."��ҵ��",
	temp_tb."����",
	(
	CASE
			
			WHEN temp_tb."����" LIKE'%��' THEN
			1 
			WHEN temp_tb."����" = 'TV��Ʒ' THEN
			2 
			WHEN temp_tb."����" = 'IC��Ʒ' THEN
			3 
			WHEN temp_tb."����" = 'TV' THEN
			4 
			WHEN temp_tb."����" = '��ý��' THEN
			5 
			WHEN temp_tb."����" = 'CTL' THEN
			6 
		END 
		) AS ����
		,
		concat ( round(( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" ) :: NUMERIC * 100 ), '%' ) AS ȥ��ת����,
		concat ( round(( temp_tb."�������۽��" / temp_tb."���궩�����" ) :: NUMERIC * 100 ), '%' ) AS ����ת����,
		concat (
			round((( temp_tb."�������۽��" / temp_tb."���궩�����" ) - ( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" )) :: NUMERIC * 100 ),
			'%' 
		) AS ���� 
	FROM
		(
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."����ҵ��" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ"
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')	
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."����ҵ��" UNION ALL
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."��Ʒ����" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ"
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')	
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."��Ʒ����" UNION ALL
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."����" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ"
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')	
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."����" 
		) AS temp_tb 
	WHERE
		temp_tb."��ҵ��" = '��������Ʒ��' 
ORDER BY
����;
	
	
	
SELECT
	temp_tb."��ҵ��",
	temp_tb."����",
	(
	CASE
			
			WHEN temp_tb."����" LIKE'%��' THEN
			1 
			WHEN temp_tb."����" = 'TV��Ʒ' THEN
			2 
			WHEN temp_tb."����" = 'IC��Ʒ' THEN
			3 
			WHEN temp_tb."����" = 'TV' THEN
			4 
			WHEN temp_tb."����" = '��ý��' THEN
			5 
			WHEN temp_tb."����" = 'CTL' THEN
			6 
		END 
		) AS ����
		,
		concat ( round(( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" ) :: NUMERIC * 100 ), '%' ) AS ȥ��ת����,
		concat ( round(( temp_tb."�������۽��" / temp_tb."���궩�����" ) :: NUMERIC * 100 ), '%' ) AS ����ת����,
		concat (
			round((( temp_tb."�������۽��" / temp_tb."���궩�����" ) - ( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" )) :: NUMERIC * 100 ),
			'%' 
		) AS ���� 
	FROM
		(
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."����ҵ��" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ" 
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."����ҵ��" UNION ALL
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."��Ʒ����" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ"
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')	
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."��Ʒ����" UNION ALL
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."����" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ"
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')	
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."����" 
		) AS temp_tb 
	WHERE
		temp_tb."��ҵ��" = '����Ʒ���ײ�' 
ORDER BY
����;
	
	
	
SELECT
	temp_tb."��ҵ��",
	temp_tb."����",
	(
	CASE
			
			WHEN temp_tb."����" LIKE'%��' THEN
			1 
			WHEN temp_tb."����" = 'TV��Ʒ' THEN
			2 
			WHEN temp_tb."����" = 'IC��Ʒ' THEN
			3 
			WHEN temp_tb."����" = 'TV' THEN
			4 
			WHEN temp_tb."����" = '��ý��' THEN
			5 
			WHEN temp_tb."����" = 'CTL' THEN
			6 
		END 
		) AS ����
		,
		concat ( round(( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" ) :: NUMERIC * 100 ), '%' ) AS ȥ��ת����,
		concat ( round(( temp_tb."�������۽��" / temp_tb."���궩�����" ) :: NUMERIC * 100 ), '%' ) AS ����ת����,
		concat (
			round((( temp_tb."�������۽��" / temp_tb."���궩�����" ) - ( temp_tb."ȥ�����۽��" / temp_tb."ȥ�궩�����" )) :: NUMERIC * 100 ),
			'%' 
		) AS ���� 
	FROM
		(
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."����ҵ��" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ"
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')	
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."����ҵ��" UNION ALL
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."��Ʒ����" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ"
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')	
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."��Ʒ����" UNION ALL
		SELECT
			"����Դ"."����ҵ��" AS ��ҵ��,
			"����Դ"."����" AS ����,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."�������" ELSE NULL END ) AS ȥ�궩�����,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
			SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."�������" ELSE NULL END ) AS ���궩����� 
		FROM
			"����Դ"
		WHERE "����Դ"."��˾" IN ('���ӹ��﹫˾','������')	
		GROUP BY
			"����Դ"."����ҵ��",
			"����Դ"."����" 
		) AS temp_tb 
	WHERE
		temp_tb."��ҵ��" = '�鱦��Ʒ��' 
ORDER BY
����;