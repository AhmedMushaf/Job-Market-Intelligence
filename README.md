# 📊 Job Market Intelligence — Data Analyst Hiring Trends

**End-to-end data analytics project analyzing real job postings from Naukri**

This project scrapes real job listings, cleans and models skill demand, performs SQL analytics, and visualizes hiring trends using Power BI.  
Built as a complete industry-style data pipeline.

---

## 🚀 Project Overview

The goal of this project is to understand:

- Which skills are most demanded for data analyst roles  
- How salary varies by skills and experience  
- What skill combinations lead to higher pay  
- Real hiring trends from job market data  

This is a **full pipeline project** from web scraping → analytics → dashboard.

---

## 🧱 Pipeline Architecture

# 📊 Job Market Intelligence — Data Analyst Hiring Trends

**End-to-end data analytics project analyzing real job postings from Naukri**

This project scrapes real job listings, cleans and models skill demand, performs SQL analytics, and visualizes hiring trends using Power BI.  
Built as a complete industry-style data pipeline.

---

## 🚀 Project Overview

The goal of this project is to understand:

- Which skills are most demanded for data analyst roles  
- How salary varies by skills and experience  
- What skill combinations lead to higher pay  
- Real hiring trends from job market data  

This is a **full pipeline project** from web scraping → analytics → dashboard.

---

## 🧱 Pipeline Architecture

Web Scraping (Selenium)

↓

Raw Job URLs + Job Details

↓

Data Cleaning & Skill Modeling (Pandas)

↓

MySQL Database

↓

Advanced SQL Analytics

↓

Power BI Dashboard


---

## 🛠 Tech Stack

**Languages & Tools**
- Python  
- SQL (MySQL)  
- Power BI  

**Libraries**
- Selenium  
- Pandas  
- NumPy  
- Matplotlib / Seaborn  
- MySQL Connector  

---

## 📂 Project Structure

job-market-intelligence

│

├── scraping/

│ ├── search_naukri.py

│ ├── job_details_scraper.py

│ ├── run_scraper.py

│ ├── config.py

│ └── utils.py

│

├── analysis/

│ ├── data_cleaning.py

│ └── phase_6_eda.ipynb

│

├── database/

│ ├── insert_mysql.py

│ └── sql_query.sql

│

├── dashboard/

│ └── power_bi_dashboard.pbix

| └──power_bi_dashboard.png

│

├── data/

│ └── processed/

│ └── job_details_cleaned_sample.csv

│

├── requirements.txt

└── README.md

---

## 📊 Dataset

- Source: Naukri.com  
- Jobs scraped: **527**  
- Cities: Hyderabad, Bengaluru, Mumbai  
- Role: Data Analyst  

---

## 🔎 Key Insights

- SQL appears in ~60% of job postings  
- Python appears in ~40%  
- SQL + Python roles offer higher salaries  
- Entry-level roles dominate hiring volume  
- Visualization tools (Power BI/Tableau) widely required  
- Senior roles demand ML + cloud skills  

---

## 🧠 Skill Modeling Approach

Instead of counting skills blindly, this project models skills in layers:

- Role requirement → Data Analysis  
- Core tools → SQL, Python, Excel  
- BI tools → Power BI, Tableau  
- Advanced → ML, Statistics  
- Cloud → AWS, Azure  

Also analyzes **skill combinations** and their salary impact.

---

## 🗄 SQL Analytics

Key queries performed:

- Skill demand percentage  
- Avg salary per skill  
- Salary by experience level  
- Tool combination impact  
- Senior role skill demand  

Example:

sql

SELECT 

CASE 

    WHEN SQL=1 AND Python=1 THEN 'SQL + Python'
    WHEN SQL=1 THEN 'SQL only'
    WHEN Python=1 THEN 'Python only'
    ELSE 'Other'
END AS skill_group,

AVG(salary_lpa_min) avg_salary

FROM jobs

GROUP BY skill_group;

---

📈 Power BI Dashboard

The dashboard includes:
- Job count & median salary KPIs
- Salary distribution
- Salary vs experience
- Skill demand chart
- Skill vs salary
- Tool combination impact
- Hiring insights panel

File included:

dashboard/power_bi_dashboard.pbix
---

⚙️ How to Run

1️⃣ Install dependencies

pip install -r requirements.txt

2️⃣ Run scraper

python run_scraper.py

3️⃣ Clean data

python data_cleaning.py

4️⃣ Insert into MySQL

python insert_mysql.py

5️⃣ Open dashboard

Open Power BI file:

power_bi_dashboard.pbix

---

📌 Future Improvements
- Add automated daily scraping
- Deploy dashboard online
- Add role comparison (Data Scientist vs Analyst)
- Add NLP skill extraction
- Add city-wise comparison with full dataset
---

👨‍💻 Author

Ahmed Mushaf

Data Analyst | Python | SQL | Power BI



