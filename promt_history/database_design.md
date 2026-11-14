## Database Design – AI Prompt History

The database schema was designed iteratively with AI assistance. Instead of generating the complete database in a single prompt, I followed a step-by-step approach to understand the requirements, identify entities, define relationships, refine attributes, and improve the database structure.

The following prompts represent the major stages of my database design process.

### 1. Understanding the problem and identifying nouns

**Prompt:**

> First, understand the complete Customer Complaint Management and Resolution System problem statement. Don't generate any SQL code now. Identify all the important nouns and business entities from the problem statement. Explain why each noun is important and which ones can become database tables. Also identify the master data, transactional data, and historical data separately.

**Outcome:**
- Identified customers, complaints, agents, teams, categories, orders, products, messages, resolutions, and surveys.
- Separated master/reference entities from transactional and historical entities.
- Identified the need to maintain complaint history and ownership changes.

### 2. Converting identified nouns into tables

**Prompt:**

> Based on the nouns we identified, let's decide the database tables. I don't want to create unnecessary tables. Explain the purpose of each table, its responsibility, and how it is connected with other tables. Also identify which entities have one-to-many and many-to-many relationships. Before writing SQL, let's finalize the table list.

**Outcome:**
- Defined the initial table structure.
- Identified relationships between customers, orders, products, complaints, and agents.
- Identified the need for a bridge table between orders and products.

### 3. Defining attributes for each table

**Prompt:**

> Now let's take each table one by one and identify the required attributes. For every column, explain why it is needed, its data type, whether it should be nullable or NOT NULL, and whether it needs a primary key or foreign key. Consider the actual complaint workflow and future reporting requirements. Don't add attributes just for the sake of adding them.

**Outcome:**
- Defined primary keys and foreign keys.
- Added business attributes and timestamps.
- Considered complaint status, priority, assignment, SLA deadlines, and resolution details.
- Used deterministic IDs generated through Python.

### 4. Designing relationships and normalization

**Prompt:**

> Review the complete table structure and check whether the database is properly normalized. I want to avoid duplicate data and update, insert, and delete anomalies. Check whether any table contains multiple responsibilities or repeated information. Explain where we need separate tables and bridge tables. Also explain the relationships before changing the schema.

**Outcome:**
- Separated order items from orders and products.
- Separated complaint messages, assignments, status history, and SLA events.
- Maintained ownership and resolution history rather than overwriting previous records.
- Improved separation of master data and transactional data.

### 5. Adding constraints and data integrity

**Prompt:**

> Now review the attributes and relationships from a PostgreSQL perspective. Add appropriate PRIMARY KEY, FOREIGN KEY, UNIQUE, NOT NULL, CHECK constraints, and default values. Think about invalid complaint states, incorrect timestamps, invalid priority values, and inconsistent order item values. I want the database to prevent invalid data wherever possible.

**Outcome:**
- Added constraints for status, priority, severity, customer tier, and order status.
- Added positive-value checks for prices, quantities, and SLA durations.
- Added timestamp consistency checks where applicable.
- Used nullable customer references where the complaint investigation scenario requires testing missing customer information.

### 6. Designing complaint history and SLA tracking

**Prompt:**

> I want to track the complete lifecycle of every complaint. A complaint can be assigned to different agents, its status can change multiple times, and its SLA can be paused, resumed, escalated, or breached. How should we design the tables to preserve the complete history? Don't just store the latest status or assigned agent. Suggest a proper relational design.

**Outcome:**
- Introduced complaint assignment history.
- Introduced complaint status history.
- Separated SLA clocks and SLA events.
- Added resolution cycles and customer surveys.
- Designed the system to support auditability and lifecycle tracking.

### 7. Designing decision logs, exceptions, and ground truth

**Prompt:**

> This project also needs to identify invalid or suspicious complaint records and evaluate whether our detection logic is working correctly. How should we store decision logs, validation exceptions, and ground truth separately? I don't want the ground truth data to influence the actual complaint classification or detection logic. Suggest a clean database design for this.

**Outcome:**
- Added decision logs to record system decisions.
- Added exception cases to store detected data-quality issues.
- Created a separate `gt` schema for ground truth.
- Kept evaluation labels separate from operational data.

### 8. Reviewing the complete schema

**Prompt:**

> Now review the complete database design as a senior PostgreSQL database designer. Check whether any important entity or relationship is missing. Identify unnecessary columns, missing constraints, data duplication, and possible future problems. Don't rewrite everything immediately. First give me the issues and suggestions, then we can finalize the schema.

**Outcome:**
- Reviewed the complete table structure.
- Refined relationships and constraints.
- Finalized 19 operational tables in the `public` schema and one ground truth table in the `gt` schema.

### 9. Asking for index recommendations

**Prompt:**

> The table structure is finalized. Now let's discuss indexing separately. Identify which columns need indexes based on foreign-key relationships and common application queries. Consider complaint filtering by customer, status, priority, category, and creation date. Also consider joins and historical queries. Explain why each index is required. Don't mix index creation with table creation SQL.

**Outcome:**
- Identified indexes on frequently queried foreign keys.
- Added indexes for common complaint filters and historical lookups.
- Separated index creation into independent SQL files.

### 10. Organizing SQL files and Python execution

**Prompt:**

> Now divide the finalized database schema into multiple SQL files based on table responsibilities. I want separate files for master/reference tables, orders, complaint workflow, and traceability/ground truth. Keep indexes in separate files. Also provide one Python script to execute the SQL files in the correct dependency order using my Neon PostgreSQL connection. I am using pg8000 because psycopg binary installation was blocked on my Windows environment.

**Outcome:**
- Organized SQL definitions into separate files.
- Created a Python runner using `pg8000`, `python-dotenv`, and `sqlparse`.
- Kept indexes independently executable.
- Used Neon PostgreSQL as the database environment.

---


