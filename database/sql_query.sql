-- CREATE DATABASE job_market;
USE job_market;

SELECT COUNT(*) AS total_jobs
FROM jobs;

SELECT experience_level, COUNT(*) AS jobs
FROM jobs
GROUP BY experience_level
ORDER BY jobs DESC;

SELECT
SUM(`SQL`) AS sql_demand,
SUM(`Python`) AS python_demand,
SUM(`Excel`) AS excel_demand,
SUM(`Power BI`) AS powerbi_demand,
SUM(`Tableau`) AS tableau_demand
FROM jobs;

SELECT 'SQL' AS skill,
       AVG(salary_lpa_min) AS avg_salary
FROM jobs
WHERE `SQL` = 1

UNION ALL

SELECT 'Python' AS skill,
       AVG(salary_lpa_min) AS avg_salary
FROM jobs
WHERE `Python` = 1

UNION ALL

SELECT 'Power BI' AS skill,
       AVG(salary_lpa_min) AS avg_salary
FROM jobs
WHERE `Power BI` = 1;

SELECT 
core_tools_score,
COUNT(*) AS jobs
FROM jobs
GROUP BY core_tools_score
ORDER BY core_tools_score DESC;

SELECT 
advanced_score,
AVG(salary_lpa_min) AS avg_salary
FROM jobs
GROUP BY advanced_score
ORDER BY advanced_score DESC;

CREATE VIEW job_analytics AS
SELECT
    `experience_level`,
    `salary_lpa_min`,
    `SQL`,
    `Python`,
    `Excel`,
    `Power BI`,
    `Tableau`,
    `Machine Learning`,
    `Statistics`,
    `AWS`,
    `Azure`,
    `Data visualization`,
    `core_tools_score`,
    `bi_tools_score`,
    `advanced_score`,
    `cloud_score`
FROM jobs;

CREATE OR REPLACE VIEW skill_salary AS
SELECT 'SQL' AS skill, AVG(salary_lpa_min) AS avg_salary FROM jobs WHERE `SQL`=1
UNION
SELECT 'Python', AVG(salary_lpa_min) FROM jobs WHERE `Python`=1
UNION
SELECT 'Power BI', AVG(salary_lpa_min) FROM jobs WHERE `Power BI`=1
UNION
SELECT 'Tableau', AVG(salary_lpa_min) FROM jobs WHERE `Tableau`=1;

SELECT
ROUND(AVG(salary_lpa_min),2) AS avg_salary
FROM job_analytics
WHERE salary_lpa_min IS NOT NULL;

SELECT
ROUND(SUM(`SQL`)/COUNT(*)*100,1) AS sql_demand,
ROUND(SUM(Python)/COUNT(*)*100,1) AS python_demand,
ROUND(SUM(Excel)/COUNT(*)*100,1) AS excel_demand
FROM job_analytics;

SELECT 'SQL' AS skill, SUM(`SQL`) AS demand FROM job_analytics
UNION ALL
SELECT 'Python', SUM(Python) FROM job_analytics
UNION ALL
SELECT 'Excel', SUM(Excel) FROM job_analytics
UNION ALL
SELECT 'Power BI', SUM(`Power BI`) FROM job_analytics
UNION ALL
SELECT 'Tableau', SUM(Tableau) FROM job_analytics
ORDER BY demand DESC;

SELECT
experience_level,
COUNT(*) AS jobs
FROM job_analytics
GROUP BY experience_level
ORDER BY jobs DESC;

SELECT
experience_level,
ROUND(AVG(salary_lpa_min),2) AS avg_salary
FROM job_analytics
GROUP BY experience_level;

SELECT
'SQL' AS skill,
ROUND(AVG(salary_lpa_min),2) AS avg_salary
FROM job_analytics WHERE `SQL` = 1

UNION ALL

SELECT
'Python',
ROUND(AVG(salary_lpa_min),2)
FROM job_analytics WHERE Python = 1

UNION ALL

SELECT
'Power BI',
ROUND(AVG(salary_lpa_min),2)
FROM job_analytics WHERE `Power BI` = 1;

SELECT
core_tools_score,
COUNT(*) AS job_count
FROM job_analytics
GROUP BY core_tools_score
ORDER BY core_tools_score DESC;

SELECT
SUM(`Machine Learning`) AS ml_jobs,
SUM(AWS) AS aws_jobs,
SUM(Azure) AS azure_jobs
FROM job_analytics;

SELECT
`SQL` + Python + `Power BI` AS combo_score,
COUNT(*) AS jobs
FROM job_analytics
GROUP BY combo_score
ORDER BY combo_score DESC;
