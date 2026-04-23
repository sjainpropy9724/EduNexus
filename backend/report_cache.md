# Curriculum Amendment Report
**Department:** Computer Science & Engineering  
**Audit Type:** Graph-RAG Automated Analysis  
**Date:** April 23, 2026

## 1. Executive Summary
The Graph-RAG automated audit reveals critical deficiencies in the Computer Science & Engineering curriculum's alignment with current industry demands. The Curriculum Alignment Score (CAS) stands at a notably low 4.93%, indicating that only a negligible portion of in-demand market skills are adequately covered. Concurrently, the Pedagogical Integrity Score (PIS) of 76.11% suggests moderate, but identifiable, structural issues within course prerequisites and content flow, highlighted by a significant number of broken prerequisite chains. Overall, the current curriculum structure is poorly positioned to equip graduates with the essential competencies required by the modern technology landscape, necessitating immediate and comprehensive revisions to ensure student competitiveness and educational effectiveness.

## 2. Quantitative Findings
The following table summarizes the key metrics derived from the Graph-RAG audit:

| Metric                                  | Value        | Notes                                                              |
| :-------------------------------------- | :----------- | :----------------------------------------------------------------- |
| Curriculum Alignment Score (CAS)        | 4.93%        | Percentage of market demand covered by the curriculum.             |
| Pedagogical Integrity Score (PIS)       | 76.11%       | Reflects the coherence and structural soundness of the curriculum.  |
| Total Market Demand Points              | 7,359,655    | Aggregate demand for skills identified in the job market.          |
| Covered Market Demand Points            | 362,475      | Demand points for skills currently addressed in the curriculum.    |
| Percentage of Market Demand Covered     | 4.93%        | Direct measure of curriculum relevance to market.                  |
| Total Prerequisite Chains               | 1,377        | Total logical dependencies between courses/topics.                 |
| Broken Prerequisite Chains              | 329          | Instances where prerequisites are not adequately met or sequenced.  |
| Percentage of Broken Prerequisite Chains| 23.89%       | Indicates structural pedagogical issues.                           |

## 3. Critical Market Gaps
The audit identified several significant skill gaps where the current curriculum fails to meet industry demand. These are listed below by market demand, inferring their structural importance and priority.

*   **Data Structures and Algorithms**
    *   **Demand Score:** 2,738,140
    *   **Structural Importance:** This foundational skill is critical for efficient problem-solving, software development, and understanding computational complexity across all domains of computer science. Its absence represents a core deficiency.
    *   **Priority Ranking:** 1 (Highest demand, most foundational).

*   **Linux**
    *   **Demand Score:** 850,356
    *   **Structural Importance:** Essential operating system knowledge for server management, cloud computing, development environments, and cybersecurity, widely used across industry.
    *   **Priority Ranking:** 2 (High demand, broad applicability).

*   **.NET**
    *   **Demand Score:** 505,218
    *   **Structural Importance:** A core framework for enterprise application development, particularly prevalent in Windows-centric ecosystems and significant within cloud-native architectures.
    *   **Priority Ranking:** 3 (Significant demand, enterprise focus).

*   **Java EE**
    *   **Demand Score:** 452,782
    *   **Structural Importance:** Forms the basis for large-scale, robust enterprise Java applications, crucial for backend development and distributed systems.
    *   **Priority Ranking:** 4 (Significant demand, enterprise focus).

*   **JavaScript**
    *   **Demand Score:** 394,142
    *   **Structural Importance:** Indispensable for modern web development (frontend and increasingly backend with Node.js), interactive applications, and full-stack roles.
    *   **Priority Ranking:** 5 (High demand, pervasive in web technologies).

*   **Spring Framework**
    *   **Demand Score:** 363,590
    *   **Structural Importance:** The dominant framework for building enterprise-grade Java applications, often used in conjunction with Java EE for complex systems.
    *   **Priority Ranking:** 6 (High demand, enterprise Java ecosystem).

*   **HTML**
    *   **Demand Score:** 361,884
    *   **Structural Importance:** The foundational markup language for all web content, critical for web design and development, forming the structure upon which web applications are built.
    *   **Priority Ranking:** 7 (High demand, fundamental web technology).

## 4. Actionable Interventions
To address the identified market gaps, specific interventions are recommended for existing courses based on their affinity scores and contextual overlaps.

*   **Missing Skill: Data Structures and Algorithms**
    *   **Course to Modify:** Programming for Data Science
    *   **Rationale:** This course exhibits the highest affinity score (58) for integrating Data Structures and Algorithms, supported by an existing contextual overlap with "SQL." This suggests a natural connection to algorithmic thinking in data manipulation.
    *   **Insertion Point:** Integrate core data structures (e.g., arrays, lists, trees, hash tables) and fundamental algorithms (e.g., sorting, searching) within existing modules that address data processing and query optimization, particularly where "SQL" is taught.

*   **Missing Skill: Linux**
    *   **Course to Modify:** Programming for Data Science
    *   **Rationale:** With an affinity score of 602, "Programming for Data Science" presents the strongest contextual overlap, specifically with "SQL." This course provides an opportunity to introduce command-line environments critical for data operations.
    *   **Insertion Point:** Introduce Linux command-line essentials, scripting, and file system navigation in early practical sessions or laboratory exercises, particularly those involving "SQL" database interactions or server-side data processing.

*   **Missing Skill: .NET**
    *   **Course to Modify:** Programming for Data Science
    *   **Rationale:** This course has the highest affinity score (448) for .NET, indicated by an overlapping context with "SQL." While .NET is a broader framework, an initial exposure can be relevant to data-centric applications.
    *   **Insertion Point:** Introduce key .NET concepts or the use of .NET-based tools for data access and manipulation in modules related to "SQL" or relational databases, providing a foundational understanding.

*   **Missing Skill: Java EE**
    *   **Course to Modify:** Programming for Data Science
    *   **Rationale:** "Programming for Data Science" shows the highest affinity score (202), with an overlapping context with "SQL." While not a direct match, the course can serve as an entry point for enterprise programming concepts.
    *   **Insertion Point:** Introduce fundamental Java EE concepts or the use of Java-based enterprise tools for data-driven web applications in advanced topics that build upon "SQL" or distributed data processing.

*   **Missing Skill: JavaScript**
    *   **Course to Modify:** Programming for Data Science
    *   **Rationale:** Possessing the highest affinity score (546), with overlaps in "SQL" and "Relational Databases," this course can integrate JavaScript for data visualization or interactive web interfaces.
    *   **Insertion Point:** Incorporate JavaScript for frontend data presentation, API interaction, or basic web application development in modules that utilize "SQL" or interact with "Relational Databases" for data retrieval and display.

*   **Missing Skill: Spring Framework**
    *   **Course to Modify:** IoT Architectures and Protocols / BCSE310L IoT Architectures and Protocols
    *   **Rationale:** Both "IoT Architectures and Protocols" and "BCSE310L IoT Architectures and Protocols" share the highest affinity score (98), with overlapping context in "REST API." Spring is highly relevant for building robust APIs.
    *   **Insertion Point:** Introduce Spring Boot for developing RESTful APIs within topics covering "REST API" design and implementation in IoT architectures, demonstrating its utility in connected device communication.

*   **Missing Skill: HTML**
    *   **Course to Modify:** Programming for Data Science
    *   **Rationale:** With an affinity score of 414 and overlap with "SQL," "Programming for Data Science" can incorporate HTML for basic web reporting or dashboarding of data.
    *   **Insertion Point:** Introduce fundamental HTML for creating simple web pages to display data results or interactive reports in modules where data analysis outcomes are presented, building on "SQL" queries.

## 5. Board Recommendation
Given the critically low Curriculum Alignment Score (4.93%) and the presence of significant market skill gaps coupled with pedagogical integrity issues (23.89% broken prerequisite chains), the Board of Studies is urged to approve **Immediate** intervention. A dedicated task force should be established to implement the proposed actionable interventions by modifying the identified courses and to conduct a broader review of prerequisite structures. This rapid response is essential to re-align the curriculum with industry needs, enhance pedagogical coherence, and ensure the market readiness and competitiveness of our graduates.