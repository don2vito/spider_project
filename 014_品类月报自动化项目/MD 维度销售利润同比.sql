SELECT
	temp_tb."��ҵ��",
	temp_tb.MD��,
	temp_tb."ȥ�����۽��",
	temp_tb."�������۽��",
	temp_tb."ȥ����������",
	temp_tb."������������",
	concat ( round(( temp_tb."�������۽��" / temp_tb."ȥ�����۽��" - 1 ) :: NUMERIC * 100 ), '%' ) AS ���۽��ͬ��,
	concat ( round(( temp_tb."������������" / temp_tb."ȥ����������" - 1 ) :: NUMERIC * 100 ), '%' ) AS ��������ͬ�� 
FROM
	(
SELECT
	"����Դ"."����ҵ��" AS ��ҵ��,
	"����Դ"."MD��" AS MD��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."��������" ELSE NULL END ) AS ȥ����������,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."��������" ELSE NULL END ) AS ������������ 
FROM
	"����Դ" 
WHERE
	"����Դ"."��˾" IN ( '���ӹ��﹫˾', '������' ) 
GROUP BY
	"����Դ"."����ҵ��",
	"����Դ"."MD��" 
	) AS temp_tb 
WHERE
	temp_tb."��ҵ��" = '���߳��粿' 
	AND temp_tb."ȥ�����۽��" <> 0 
	AND concat ( round(( temp_tb."�������۽��" / temp_tb."ȥ�����۽��" - 1 ) :: NUMERIC * 100 ), '%' ) <> '%';



SELECT
	temp_tb."��ҵ��",
	temp_tb.MD��,
	temp_tb."ȥ�����۽��",
	temp_tb."�������۽��",
	temp_tb."ȥ����������",
	temp_tb."������������",
	concat ( round(( temp_tb."�������۽��" / temp_tb."ȥ�����۽��" - 1 ) :: NUMERIC * 100 ), '%' ) AS ���۽��ͬ��,
	concat ( round(( temp_tb."������������" / temp_tb."ȥ����������" - 1 ) :: NUMERIC * 100 ), '%' ) AS ��������ͬ�� 
FROM
	(
SELECT
	"����Դ"."����ҵ��" AS ��ҵ��,
	"����Դ"."MD��" AS MD��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."��������" ELSE NULL END ) AS ȥ����������,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."��������" ELSE NULL END ) AS ������������ 
FROM
	"����Դ" 
WHERE
	"����Դ"."��˾" IN ( '���ӹ��﹫˾', '������' ) 
GROUP BY
	"����Դ"."����ҵ��",
	"����Դ"."MD��" 
	) AS temp_tb 
WHERE
	temp_tb."��ҵ��" = '��ͥͶ�ʲ�' 
	AND temp_tb."ȥ�����۽��" <> 0 
	AND concat ( round(( temp_tb."�������۽��" / temp_tb."ȥ�����۽��" - 1 ) :: NUMERIC * 100 ), '%' ) <> '%';
	
	
	
	SELECT
	temp_tb."��ҵ��",
	temp_tb.MD��,
	temp_tb."ȥ�����۽��",
	temp_tb."�������۽��",
	temp_tb."ȥ����������",
	temp_tb."������������",
	concat ( round(( temp_tb."�������۽��" / temp_tb."ȥ�����۽��" - 1 ) :: NUMERIC * 100 ), '%' ) AS ���۽��ͬ��,
	concat ( round(( temp_tb."������������" / temp_tb."ȥ����������" - 1 ) :: NUMERIC * 100 ), '%' ) AS ��������ͬ�� 
FROM
	(
SELECT
	"����Դ"."����ҵ��" AS ��ҵ��,
	"����Դ"."MD��" AS MD��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."��������" ELSE NULL END ) AS ȥ����������,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."��������" ELSE NULL END ) AS ������������ 
FROM
	"����Դ" 
WHERE
	"����Դ"."��˾" IN ( '���ӹ��﹫˾', '������' ) 
GROUP BY
	"����Դ"."����ҵ��",
	"����Դ"."MD��" 
	) AS temp_tb 
WHERE
	temp_tb."��ҵ��" = '����������' 
	AND temp_tb."ȥ�����۽��" <> 0 
	AND concat ( round(( temp_tb."�������۽��" / temp_tb."ȥ�����۽��" - 1 ) :: NUMERIC * 100 ), '%' ) <> '%';
	
	
	
	SELECT
	temp_tb."��ҵ��",
	temp_tb.MD��,
	temp_tb."ȥ�����۽��",
	temp_tb."�������۽��",
	temp_tb."ȥ����������",
	temp_tb."������������",
	concat ( round(( temp_tb."�������۽��" / temp_tb."ȥ�����۽��" - 1 ) :: NUMERIC * 100 ), '%' ) AS ���۽��ͬ��,
	concat ( round(( temp_tb."������������" / temp_tb."ȥ����������" - 1 ) :: NUMERIC * 100 ), '%' ) AS ��������ͬ�� 
FROM
	(
SELECT
	"����Դ"."����ҵ��" AS ��ҵ��,
	"����Դ"."MD��" AS MD��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."��������" ELSE NULL END ) AS ȥ����������,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."��������" ELSE NULL END ) AS ������������ 
FROM
	"����Դ" 
WHERE
	"����Դ"."��˾" IN ( '���ӹ��﹫˾', '������' ) 
GROUP BY
	"����Դ"."����ҵ��",
	"����Դ"."MD��" 
	) AS temp_tb 
WHERE
	temp_tb."��ҵ��" = '���з��β�' 
	AND temp_tb."ȥ�����۽��" <> 0 
	AND concat ( round(( temp_tb."�������۽��" / temp_tb."ȥ�����۽��" - 1 ) :: NUMERIC * 100 ), '%' ) <> '%';
	
	
	
	SELECT
	temp_tb."��ҵ��",
	temp_tb.MD��,
	temp_tb."ȥ�����۽��",
	temp_tb."�������۽��",
	temp_tb."ȥ����������",
	temp_tb."������������",
	concat ( round(( temp_tb."�������۽��" / temp_tb."ȥ�����۽��" - 1 ) :: NUMERIC * 100 ), '%' ) AS ���۽��ͬ��,
	concat ( round(( temp_tb."������������" / temp_tb."ȥ����������" - 1 ) :: NUMERIC * 100 ), '%' ) AS ��������ͬ�� 
FROM
	(
SELECT
	"����Դ"."����ҵ��" AS ��ҵ��,
	"����Դ"."MD��" AS MD��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."��������" ELSE NULL END ) AS ȥ����������,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."��������" ELSE NULL END ) AS ������������ 
FROM
	"����Դ" 
WHERE
	"����Դ"."��˾" IN ( '���ӹ��﹫˾', '������' ) 
GROUP BY
	"����Դ"."����ҵ��",
	"����Դ"."MD��" 
	) AS temp_tb 
WHERE
	temp_tb."��ҵ��" = '������ʳ��' 
	AND temp_tb."ȥ�����۽��" <> 0 
	AND concat ( round(( temp_tb."�������۽��" / temp_tb."ȥ�����۽��" - 1 ) :: NUMERIC * 100 ), '%' ) <> '%';
	
	
	
	SELECT
	temp_tb."��ҵ��",
	temp_tb.MD��,
	temp_tb."ȥ�����۽��",
	temp_tb."�������۽��",
	temp_tb."ȥ����������",
	temp_tb."������������",
	concat ( round(( temp_tb."�������۽��" / temp_tb."ȥ�����۽��" - 1 ) :: NUMERIC * 100 ), '%' ) AS ���۽��ͬ��,
	concat ( round(( temp_tb."������������" / temp_tb."ȥ����������" - 1 ) :: NUMERIC * 100 ), '%' ) AS ��������ͬ�� 
FROM
	(
SELECT
	"����Դ"."����ҵ��" AS ��ҵ��,
	"����Դ"."MD��" AS MD��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."��������" ELSE NULL END ) AS ȥ����������,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."��������" ELSE NULL END ) AS ������������ 
FROM
	"����Դ" 
WHERE
	"����Դ"."��˾" IN ( '���ӹ��﹫˾', '������' ) 
GROUP BY
	"����Դ"."����ҵ��",
	"����Դ"."MD��" 
	) AS temp_tb 
WHERE
	temp_tb."��ҵ��" = '������β�' 
	AND temp_tb."ȥ�����۽��" <> 0 
	AND concat ( round(( temp_tb."�������۽��" / temp_tb."ȥ�����۽��" - 1 ) :: NUMERIC * 100 ), '%' ) <> '%';
	
	
	
	SELECT
	temp_tb."��ҵ��",
	temp_tb.MD��,
	temp_tb."ȥ�����۽��",
	temp_tb."�������۽��",
	temp_tb."ȥ����������",
	temp_tb."������������",
	concat ( round(( temp_tb."�������۽��" / temp_tb."ȥ�����۽��" - 1 ) :: NUMERIC * 100 ), '%' ) AS ���۽��ͬ��,
	concat ( round(( temp_tb."������������" / temp_tb."ȥ����������" - 1 ) :: NUMERIC * 100 ), '%' ) AS ��������ͬ�� 
FROM
	(
SELECT
	"����Դ"."����ҵ��" AS ��ҵ��,
	"����Դ"."MD��" AS MD��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."��������" ELSE NULL END ) AS ȥ����������,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."��������" ELSE NULL END ) AS ������������ 
FROM
	"����Դ" 
WHERE
	"����Դ"."��˾" IN ( '���ӹ��﹫˾', '������' ) 
GROUP BY
	"����Դ"."����ҵ��",
	"����Դ"."MD��" 
	) AS temp_tb 
WHERE
	temp_tb."��ҵ��" = '���ѷ���' 
	AND temp_tb."ȥ�����۽��" <> 0 
	AND concat ( round(( temp_tb."�������۽��" / temp_tb."ȥ�����۽��" - 1 ) :: NUMERIC * 100 ), '%' ) <> '%';
	
	
	
	SELECT
	temp_tb."��ҵ��",
	temp_tb.MD��,
	temp_tb."ȥ�����۽��",
	temp_tb."�������۽��",
	temp_tb."ȥ����������",
	temp_tb."������������",
	concat ( round(( temp_tb."�������۽��" / temp_tb."ȥ�����۽��" - 1 ) :: NUMERIC * 100 ), '%' ) AS ���۽��ͬ��,
	concat ( round(( temp_tb."������������" / temp_tb."ȥ����������" - 1 ) :: NUMERIC * 100 ), '%' ) AS ��������ͬ�� 
FROM
	(
SELECT
	"����Դ"."����ҵ��" AS ��ҵ��,
	"����Դ"."MD��" AS MD��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."��������" ELSE NULL END ) AS ȥ����������,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."��������" ELSE NULL END ) AS ������������ 
FROM
	"����Դ" 
WHERE
	"����Դ"."��˾" IN ( '���ӹ��﹫˾', '������' ) 
GROUP BY
	"����Դ"."����ҵ��",
	"����Դ"."MD��" 
	) AS temp_tb 
WHERE
	temp_tb."��ҵ��" = '���ӵ�����' 
	AND temp_tb."ȥ�����۽��" <> 0 
	AND concat ( round(( temp_tb."�������۽��" / temp_tb."ȥ�����۽��" - 1 ) :: NUMERIC * 100 ), '%' ) <> '%';
	
	
	
	SELECT
	temp_tb."��ҵ��",
	temp_tb.MD��,
	temp_tb."ȥ�����۽��",
	temp_tb."�������۽��",
	temp_tb."ȥ����������",
	temp_tb."������������",
	concat ( round(( temp_tb."�������۽��" / temp_tb."ȥ�����۽��" - 1 ) :: NUMERIC * 100 ), '%' ) AS ���۽��ͬ��,
	concat ( round(( temp_tb."������������" / temp_tb."ȥ����������" - 1 ) :: NUMERIC * 100 ), '%' ) AS ��������ͬ�� 
FROM
	(
SELECT
	"����Դ"."����ҵ��" AS ��ҵ��,
	"����Դ"."MD��" AS MD��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."��������" ELSE NULL END ) AS ȥ����������,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."��������" ELSE NULL END ) AS ������������ 
FROM
	"����Դ" 
WHERE
	"����Դ"."��˾" IN ( '���ӹ��﹫˾', '������' ) 
GROUP BY
	"����Դ"."����ҵ��",
	"����Դ"."MD��" 
	) AS temp_tb 
WHERE
	temp_tb."��ҵ��" = '�ҾӼҷĲ�' 
	AND temp_tb."ȥ�����۽��" <> 0 
	AND concat ( round(( temp_tb."�������۽��" / temp_tb."ȥ�����۽��" - 1 ) :: NUMERIC * 100 ), '%' ) <> '%';
	
	
	
	SELECT
	temp_tb."��ҵ��",
	temp_tb.MD��,
	temp_tb."ȥ�����۽��",
	temp_tb."�������۽��",
	temp_tb."ȥ����������",
	temp_tb."������������",
	concat ( round(( temp_tb."�������۽��" / temp_tb."ȥ�����۽��" - 1 ) :: NUMERIC * 100 ), '%' ) AS ���۽��ͬ��,
	concat ( round(( temp_tb."������������" / temp_tb."ȥ����������" - 1 ) :: NUMERIC * 100 ), '%' ) AS ��������ͬ�� 
FROM
	(
SELECT
	"����Դ"."����ҵ��" AS ��ҵ��,
	"����Դ"."MD��" AS MD��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."��������" ELSE NULL END ) AS ȥ����������,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."��������" ELSE NULL END ) AS ������������ 
FROM
	"����Դ" 
WHERE
	"����Դ"."��˾" IN ( '���ӹ��﹫˾', '������' ) 
GROUP BY
	"����Դ"."����ҵ��",
	"����Դ"."MD��" 
	) AS temp_tb 
WHERE
	temp_tb."��ҵ��" = '��װ���β�' 
	AND temp_tb."ȥ�����۽��" <> 0 
	AND concat ( round(( temp_tb."�������۽��" / temp_tb."ȥ�����۽��" - 1 ) :: NUMERIC * 100 ), '%' ) <> '%';
	
	
	
	SELECT
	temp_tb."��ҵ��",
	temp_tb.MD��,
	temp_tb."ȥ�����۽��",
	temp_tb."�������۽��",
	temp_tb."ȥ����������",
	temp_tb."������������",
	concat ( round(( temp_tb."�������۽��" / temp_tb."ȥ�����۽��" - 1 ) :: NUMERIC * 100 ), '%' ) AS ���۽��ͬ��,
	concat ( round(( temp_tb."������������" / temp_tb."ȥ����������" - 1 ) :: NUMERIC * 100 ), '%' ) AS ��������ͬ�� 
FROM
	(
SELECT
	"����Դ"."����ҵ��" AS ��ҵ��,
	"����Դ"."MD��" AS MD��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."��������" ELSE NULL END ) AS ȥ����������,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."��������" ELSE NULL END ) AS ������������ 
FROM
	"����Դ" 
WHERE
	"����Դ"."��˾" IN ( '���ӹ��﹫˾', '������' ) 
GROUP BY
	"����Դ"."����ҵ��",
	"����Դ"."MD��" 
	) AS temp_tb 
WHERE
	temp_tb."��ҵ��" = '��ױ����' 
	AND temp_tb."ȥ�����۽��" <> 0 
	AND concat ( round(( temp_tb."�������۽��" / temp_tb."ȥ�����۽��" - 1 ) :: NUMERIC * 100 ), '%' ) <> '%';
	
	
	
	SELECT
	temp_tb."��ҵ��",
	temp_tb.MD��,
	temp_tb."ȥ�����۽��",
	temp_tb."�������۽��",
	temp_tb."ȥ����������",
	temp_tb."������������",
	concat ( round(( temp_tb."�������۽��" / temp_tb."ȥ�����۽��" - 1 ) :: NUMERIC * 100 ), '%' ) AS ���۽��ͬ��,
	concat ( round(( temp_tb."������������" / temp_tb."ȥ����������" - 1 ) :: NUMERIC * 100 ), '%' ) AS ��������ͬ�� 
FROM
	(
SELECT
	"����Դ"."����ҵ��" AS ��ҵ��,
	"����Դ"."MD��" AS MD��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."��������" ELSE NULL END ) AS ȥ����������,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."��������" ELSE NULL END ) AS ������������ 
FROM
	"����Դ" 
WHERE
	"����Դ"."��˾" IN ( '���ӹ��﹫˾', '������' ) 
GROUP BY
	"����Դ"."����ҵ��",
	"����Դ"."MD��" 
	) AS temp_tb 
WHERE
	temp_tb."��ҵ��" = '��������Ʒ��' 
	AND temp_tb."ȥ�����۽��" <> 0 
	AND concat ( round(( temp_tb."�������۽��" / temp_tb."ȥ�����۽��" - 1 ) :: NUMERIC * 100 ), '%' ) <> '%';
	
	
	
	SELECT
	temp_tb."��ҵ��",
	temp_tb.MD��,
	temp_tb."ȥ�����۽��",
	temp_tb."�������۽��",
	temp_tb."ȥ����������",
	temp_tb."������������",
	concat ( round(( temp_tb."�������۽��" / temp_tb."ȥ�����۽��" - 1 ) :: NUMERIC * 100 ), '%' ) AS ���۽��ͬ��,
	concat ( round(( temp_tb."������������" / temp_tb."ȥ����������" - 1 ) :: NUMERIC * 100 ), '%' ) AS ��������ͬ�� 
FROM
	(
SELECT
	"����Դ"."����ҵ��" AS ��ҵ��,
	"����Դ"."MD��" AS MD��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."��������" ELSE NULL END ) AS ȥ����������,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."��������" ELSE NULL END ) AS ������������ 
FROM
	"����Դ" 
WHERE
	"����Դ"."��˾" IN ( '���ӹ��﹫˾', '������' ) 
GROUP BY
	"����Դ"."����ҵ��",
	"����Դ"."MD��" 
	) AS temp_tb 
WHERE
	temp_tb."��ҵ��" = '����Ʒ���ײ�' 
	AND temp_tb."ȥ�����۽��" <> 0 
	AND concat ( round(( temp_tb."�������۽��" / temp_tb."ȥ�����۽��" - 1 ) :: NUMERIC * 100 ), '%' ) <> '%';
	
	
	
	SELECT
	temp_tb."��ҵ��",
	temp_tb.MD��,
	temp_tb."ȥ�����۽��",
	temp_tb."�������۽��",
	temp_tb."ȥ����������",
	temp_tb."������������",
	concat ( round(( temp_tb."�������۽��" / temp_tb."ȥ�����۽��" - 1 ) :: NUMERIC * 100 ), '%' ) AS ���۽��ͬ��,
	concat ( round(( temp_tb."������������" / temp_tb."ȥ����������" - 1 ) :: NUMERIC * 100 ), '%' ) AS ��������ͬ�� 
FROM
	(
SELECT
	"����Դ"."����ҵ��" AS ��ҵ��,
	"����Դ"."MD��" AS MD��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."���۽��" ELSE NULL END ) AS ȥ�����۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."���۽��" ELSE NULL END ) AS �������۽��,
	SUM ( CASE WHEN "����Դ"."���" = '2020' THEN "����Դ"."��������" ELSE NULL END ) AS ȥ����������,
	SUM ( CASE WHEN "����Դ"."���" = '2021' THEN "����Դ"."��������" ELSE NULL END ) AS ������������ 
FROM
	"����Դ" 
WHERE
	"����Դ"."��˾" IN ( '���ӹ��﹫˾', '������' ) 
GROUP BY
	"����Դ"."����ҵ��",
	"����Դ"."MD��" 
	) AS temp_tb 
WHERE
	temp_tb."��ҵ��" = '�鱦��Ʒ��' 
	AND temp_tb."ȥ�����۽��" <> 0 
	AND concat ( round(( temp_tb."�������۽��" / temp_tb."ȥ�����۽��" - 1 ) :: NUMERIC * 100 ), '%' ) <> '%';