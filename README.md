# VaxInsight-AI-Powered-Healthcare-Journey-Analytics
VaxInsight is a Fetch.AI-powered agent designed to analyze patient journeys and sentiments in real-time, providing actionable insights for healthcare professionals. By leveraging AI, blockchain, and advanced analytics, VaxInsight helps improve healthcare decision-making, optimize resource allocation, and enhance patient engagement.
** VaxInsight: AI-Powered Healthcare Journey Analytics **
VaxInsight is a Fetch.AI-powered agent designed to analyze patient journeys and sentiments in real-time, providing actionable insights for healthcare professionals. By leveraging AI, blockchain, and advanced analytics, VaxInsight helps improve healthcare decision-making, optimize resource allocation, and enhance patient engagement.

**Features**
Real-Time Patient Journey Analysis: Tracks patient stages (e.g., hesitant, researching, accepting) and sentiments (positive, negative, neutral).

1. Scoring System: Evaluates projects across six dimensions: technology, engagement, efficiency, practicality, scalability, and impact.

2. Automated Analytics Reports: Generates periodic summaries of patient data, including stage transitions, sentiment trends, and scoring metrics.
3. Customizable Metrics: Supports custom metrics for efficiency, business value, scalability, and impact.
4. Simulated Data: Includes a built-in function to simulate patient data for testing and demos.

**Tech Stack**

- Fetch.AI: For decentralized agent deployment and communication.
- Python: Core programming language.
- uAgents Framework: For agent creation and interaction.
- Logging: For detailed tracking of analytics and processes.

**Getting Started**

Fetch.AI account
Python 3.8+
Dependencies: Install using pip install -r requirements.txt.
Setup

- Clone the Repository:
``
`git` clone <repository_url>
cd vaxinsight
`
- Install Dependencies:

`pip install -r requirements.txt`

**How to Use** 

- Simulate Data
The agent includes a simulate_test_data() function to send test patient data automatically every 10 seconds. It generates logs with patient statistics and scores.

- Send Custom Data
Use a tool like Postman or Python to send PatientJourneyEvent messages to the agent’s /submit endpoint. Example payload:

json
`
{
  "patient_id": "PATIENT001",
  "sentiment": "positive",
  "journey_stage": "accepting",
  "timestamp": "2024-12-01T10:00:00",
  "notes": "Example patient journey data",
  "metrics": {
    "process_efficiency": 0.9,
    "business_value": 0.8,
    "scalability_potential": 0.7,
    "impact_factor": 0.85
  },
  "tech_features": ["AI", "Blockchain", "Machine Learning"]
}
`
