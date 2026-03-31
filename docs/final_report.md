📊 Olist Data Intelligence: Executive & Technical Report
NTU SCTP: DSAI

🚀 1. Executive Summary
Project Objective: To transform 100k+ rows of raw, fragmented Brazilian e-commerce data into a production-grade, automated analytical engine.
💡 Key Strategic Takeaways
The 80/20 Revenue Driver: Our RFM analysis reveals that 20% of our customers (Score 5 "Whales") drive 53.3% of total revenue.
Explosive Scalability: The platform achieved 8x revenue growth between 2017 and 2018, peaking at BRL 1.2M during the November 2017 "Black Friday" event.
Revenue-at-Risk: We identified BRL 2.1M in revenue currently tied to 1-star reviews, primarily driven by logistics delays in the North and Northeast regions.

📈 2. Business Insights & Strategic Roadmap
📍 Geospatial Intelligence: The Regional Gap
Our validated geospatial analysis reveals a massive revenue concentration in the Southeast (BRL 15.4M). However, the South (BRL 3.1M) and Northeast (BRL 2.5M) represent established secondary markets with significant growth potential.
Key Finding: While the Southeast dominates, logistics costs to the South and Northeast are likely higher due to distance from current primary hubs.
Strategic Recommendation: Establish a Regional Logistics Hub in the South (Curitiba or Porto Alegre) to reduce transit times, improve customer NPS, and protect the BRL 3.1M revenue stream.
💎 Customer Value: The "Whale" Strategy
Density analysis shows São Paulo and Rio de Janeiro contain the highest concentration of "Score 5" high-value customers.
Strategic Recommendation: Launch a "Tier 1 Prime" pilot in these high-density hubs. Offering exclusive same-day delivery to these segments will lock in the majority of our revenue engine.

🏗️ 3. Technical Architecture & Decisions
We implemented a Medallion Architecture (Raw → Analytics) to ensure data lineage and security.
Python (Ingestion): Leveraged SQLAlchemy to handle complex UTF-8 encoding and chunking requirements, ensuring zero data loss during the initial load into PostgreSQL.
dbt (Incremental Transformation): To ensure scalability, we utilized Incremental Models. This reduces compute costs by only processing new records, a "Production-Ready" standard.
Great Expectations (Quality Gate): We implemented a Triple-Asset Validation Suite (Sales, Geo, Reviews). This "Circuit Breaker" prevents "silent failures" by ensuring data meets strict business logic before reaching the BI layer.

🛠️ 4. Innovation & Technical Problem Solving
The following hurdles were independently researched and resolved to qualify for the Curious & Self-Directed and Advanced Proficiency awards:
PostgreSQL Dialect Refactoring: Resolved the lack of QUALIFY support in Postgres by refactoring deduplication logic into Ranked CTEs (Common Table Expressions).
GX 1.0+ API Migration: Navigated breaking changes in the latest Great Expectations "Fluent" API, pivoting to a Code-First (Python API) approach to ensure environment portability.
Geospatial Clustering: Independently researched Brazilian Post Office (Correios) macro-region structures to engineer a custom Dim_Geography table, transforming granular zip codes into actionable "Location Intelligence."

🛡️ 5. Risk & Mitigation
Scaling Risk: Mitigated via Incremental dbt models to keep compute costs low as data grows.
Data Trust Risk: Mitigated via the Great Expectations Gate, blocking 100% of invalid $0.00 transactions.
Portability Risk: Mitigated via Decoupled .env configurations, allowing rapid migration to AWS/GCP Cloud environments.


🎯 6. Future Roadmap: Automated Governance
To maintain our 8x growth trajectory, we recommend transitioning this pipeline into a CI/CD environment via GitHub Actions. This will ensure that as Olist scales, our "Executive Dashboard" remains a Single Source of Truth protected by automated quality gates 24/7.
