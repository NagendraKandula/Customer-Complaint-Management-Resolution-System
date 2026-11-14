# Customer Complaint Management & Resolution System
# Data Dictionary

## 1. Project Overview

This project generates realistic synthetic customer complaint management data for analyzing complaint classification, assignment, resolution, SLA compliance, and customer satisfaction.

**Database:** PostgreSQL  
**Data generation language:** Python  
**Database connection:** Neon PostgreSQL  
**Random seed:** `20261022`  
**Scale:** 1.0

The dataset contains customers, products, orders, complaints, support assignments, complaint status history, resolutions, SLA records, and customer surveys.

## 2. Database Tables

| Table | Description |
|---|---|
| `teams` | Support teams responsible for handling complaints. |
| `agents` | Support employees who receive complaint assignments. |
| `categories` | Complaint categories used for classification. |
| `priority_rules` | Rules and scores used to determine complaint priority. |
| `sla_policies` | Response and resolution time targets. |
| `customers` | Customer information and contact details. |
| `products` | Products associated with customer orders and complaints. |
| `orders` | Customer purchase records. |
| `order_items` | Individual products included in orders. |
| `complaints` | Main complaint records, including category, severity, priority, and status. |
| `complaint_messages` | Communication between customers and support teams. |
| `complaint_assignments` | Assignment history showing which team and agent handled each complaint. |
| `complaint_status_history` | Historical status transitions for complaints. |
| `resolutions` | Complaint resolution records, outcomes, and refund information. |
| `sla_clocks` | SLA deadlines, response times, resolution times, and breach indicators. |
| `sla_events` | SLA lifecycle events such as pause, resume, escalation, and completion. |
| `surveys` | Customer feedback and satisfaction ratings after resolution. |
| `gt.ground_truth` | Reference labels for known injected anomalies and expected detection outcomes. |
| `exception_cases` | Records of detected data-quality exceptions. |

## 3. Important Column Descriptions

### Customers
- `customer_id`: Unique customer identifier.
- `name`: Customer name.
- `email`: Customer email address.
- `phone`: Customer contact number.

### Products
- `product_id`: Unique product identifier.
- `product_name`: Product name.
- `category`: Product category.

### Orders
- `order_id`: Unique order identifier.
- `customer_id`: Customer who placed the order.
- `order_date`: Date of purchase.
- `status`: Order lifecycle status.

### Complaints
- `complaint_id`: Unique complaint identifier.
- `customer_id`: Customer who submitted the complaint.
- `order_id`: Related customer order.
- `product_id`: Product associated with the complaint.
- `category_id`: Complaint category.
- `complaint_text`: Description of the customer's issue.
- `channel`: Source through which the complaint was submitted.
- `sentiment`: Detected customer sentiment.
- `severity`: Business impact of the complaint.
- `priority`: Priority level from P1 to P4.
- `priority_score`: Numeric priority score.
- `status`: Current complaint lifecycle status.
- `is_safety_related`: Indicates whether the complaint concerns product safety.
- `is_repeat`: Indicates whether the complaint is repeated.
- `repeat_of_complaint_id`: Reference to the original complaint.
- `reopen_count`: Number of times the complaint was reopened.
- `created_at`: Complaint creation timestamp.
- `updated_at`: Last update timestamp.

### Complaint Assignments
- `assignment_id`: Unique assignment identifier.
- `complaint_id`: Related complaint.
- `team_id`: Assigned support team.
- `agent_id`: Assigned support agent.
- `assigned_at`: Assignment timestamp.
- `ended_at`: Assignment completion timestamp.
- `assignment_reason`: Reason for assignment.

### Complaint Messages
- `message_id`: Unique message identifier.
- `complaint_id`: Related complaint.
- `sender_type`: Type of message sender.
- `message_text`: Message content.
- `created_at`: Message timestamp.

### Complaint Status History
- `history_id`: Unique status history identifier.
- `complaint_id`: Related complaint.
- `old_status`: Previous complaint status.
- `new_status`: Updated complaint status.
- `changed_at`: Status transition timestamp.

### Resolutions
- `resolution_id`: Unique resolution identifier.
- `complaint_id`: Related complaint.
- `cycle_no`: Resolution cycle number.
- `resolution_type`: Type of resolution.
- `outcome`: Resolution result.
- `resolution_notes`: Explanation of the resolution.
- `resolved_by`: Agent responsible for resolution.
- `resolved_at`: Resolution timestamp.
- `refund_amount`: Refund amount, if applicable.
- `is_final`: Indicates whether the resolution is final.

### SLA Clocks
- `sla_id`: Unique SLA identifier.
- `complaint_id`: Related complaint.
- `priority_level`: Complaint priority.
- `response_deadline`: Expected first response deadline.
- `resolution_deadline`: Expected resolution deadline.
- `first_response_at`: Actual first response timestamp.
- `resolved_at`: Actual resolution timestamp.
- `response_breached`: Indicates whether response SLA was breached.
- `resolution_breached`: Indicates whether resolution SLA was breached.
- `is_paused`: Indicates whether the SLA clock is paused.
- `total_paused_minutes`: Total paused duration.

### SLA Events
- `sla_event_id`: Unique SLA event identifier.
- `sla_id`: Related SLA record.
- `event_type`: Type of SLA event.
- `event_time`: Event timestamp.
- `reason`: Reason for the event.
- `metadata`: Additional event information.

### Surveys
- `survey_id`: Unique survey identifier.
- `complaint_id`: Related complaint.
- `resolution_id`: Related resolution.
- `sent_at`: Survey dispatch timestamp.
- `submitted_at`: Survey submission timestamp.
- `rating`: Customer satisfaction rating.
- `feedback`: Customer feedback text.

## 4. Relationships

- One customer can place multiple orders.
- One order can contain multiple order items.
- One customer can submit multiple complaints.
- A complaint can reference an order and product.
- A complaint can have multiple messages and status history records.
- A complaint can have multiple assignment history records.
- A complaint can have multiple resolution cycles.
- A complaint has an associated SLA clock and multiple SLA events.
- A resolution can have an associated customer survey.
- Support teams contain multiple agents.

## 5. Data Quality and Anomaly Scenarios

Six intentional anomalies are injected into the generated dataset:

| # | Anomaly | Description |
|---|---|---|
| 1 | COMPLAINT_NO_CUSTOMER | Complaint has a missing customer reference. |
| 2 | RESOLUTION_BEFORE_COMPLAINT | Resolution timestamp occurs before complaint creation. |
| 3 | SLA_PAUSE_INCORRECT | SLA pause information is inconsistent. |
| 4 | REPEAT_NOT_LINKED | Repeated complaint is not linked to its original complaint. |
| 5 | SAFETY_LOW_QUEUE | Safety-related complaint receives an inappropriate low-priority assignment. |
| 6 | SURVEY_BEFORE_CLOSURE | Survey is sent before the complaint creation/closure timeline is valid. |

The `gt.ground_truth` table and exported `ground_truth.csv` contain the reference labels for these scenarios.

**Important:** Ground-truth records are evaluation references only. They must not be used as input features for anomaly detection.

## 6. Data Generation Configuration

| Parameter | Value |
|---|---|
| Database | Neon PostgreSQL |
| Random seed | 20261022 |
| Scale factor | 1.0 |
| Customers | 5,000 |
| Products | 100 |
| Orders | 8,000 |
| Complaints | 2,000 |
| Intentional anomalies | 6 |

## 7. Output Files

- `output/generated_data/`: CSV exports of generated database tables.
- `output/ground_truth.csv`: Known anomaly reference records.
- `output/validation_report.txt`: Data validation results.

## 8. Reproducibility

The project uses a fixed random seed (`20261022`) to support deterministic synthetic data generation.

For reproducibility verification, generate a fresh dataset in a separate clean database using the same seed and configuration, export the resulting tables, and compare row counts and SHA-256 checksums against the original dataset.