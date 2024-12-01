from uagents import Model, Context, Agent, Protocol
from uagents.setup import fund_agent_if_low
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List, Union
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='vaxinsight.log'
)

class JourneyStage(str, Enum):
    HESITANT = "hesitant"
    RESEARCHING = "researching"
    CONSULTING = "consulting"
    ACCEPTING = "accepting"
    COMPLETED = "completed"

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class ProjectScore(Model):
    technology_score: int
    engagement_score: int
    efficiency_score: int
    practicality_score: int
    scalability_score: int
    impact_score: int
    
    def total_score(self) -> int:
        return (self.technology_score + self.engagement_score + 
                self.efficiency_score + self.practicality_score + 
                self.scalability_score + self.impact_score)

class PatientJourneyEvent(Model):
    patient_id: str
    sentiment: Sentiment
    journey_stage: JourneyStage
    timestamp: datetime
    notes: Optional[str]
    metrics: Optional[Dict[str, Union[float, int]]] = {}  # Allow numeric metrics
    tech_features: Optional[List[str]] = None  # Separate non-numeric field
    score: Optional[ProjectScore] = None

class PatientAnalytics:
    def __init__(self):
        self.journey_stats: Dict[str, Dict[str, int]] = {}
        self.sentiment_history: List[Dict] = []
    
    def update_stats(self, event: PatientJourneyEvent):
        if event.patient_id not in self.journey_stats:
            self.journey_stats[event.patient_id] = {
                "stage_changes": 0,
                "positive_sentiments": 0,
                "negative_sentiments": 0
            }
        
        self.journey_stats[event.patient_id]["stage_changes"] += 1
        if event.sentiment == Sentiment.POSITIVE:
            self.journey_stats[event.patient_id]["positive_sentiments"] += 1
        elif event.sentiment == Sentiment.NEGATIVE:
            self.journey_stats[event.patient_id]["negative_sentiments"] += 1
        
        self.sentiment_history.append({
            "timestamp": event.timestamp,
            "patient_id": event.patient_id,
            "sentiment": event.sentiment,
            "stage": event.journey_stage
        })

agent = Agent(
    name="VaxInsight_Enhanced",
    port=8000,
    endpoint=["http://127.0.0.1:8000/submit"],
)

fund_agent_if_low(agent.wallet.address())
protocol = Protocol()
analytics = PatientAnalytics()

@protocol.on_message(model=PatientJourneyEvent)
async def handle_patient_journey(ctx: Context, sender: str, msg: PatientJourneyEvent):
    """Handle incoming patient journey events with enhanced logging and analytics."""
    logging.info(f"New journey event received - Patient: {msg.patient_id}")
    logging.debug(f"Event details: {json.dumps(msg.dict(), default=str)}")
    
    # Update analytics
    analytics.update_stats(msg)
    
    # Calculate project scores
    project_score = ProjectScore(
        technology_score=calculate_technology_score(msg),
        engagement_score=calculate_engagement_score(msg),
        efficiency_score=calculate_efficiency_score(msg),
        practicality_score=calculate_practicality_score(msg),
        scalability_score=calculate_scalability_score(msg),
        impact_score=calculate_impact_score(msg)
    )
    
    # Log detailed metrics
    logging.info(f"""
    Patient Journey Metrics:
    - Patient ID: {msg.patient_id}
    - Current Stage: {msg.journey_stage}
    - Sentiment: {msg.sentiment}
    - Technology Score: {project_score.technology_score}/5
    - Engagement Score: {project_score.engagement_score}/5
    - Efficiency Score: {project_score.efficiency_score}/5
    - Practicality Score: {project_score.practicality_score}/5
    - Scalability Score: {project_score.scalability_score}/5
    - Impact Score: {project_score.impact_score}/5
    - Total Score: {project_score.total_score()}/30
    """)

# Scoring functions
def calculate_technology_score(event: PatientJourneyEvent) -> int:
    # Placeholder logic
    return min(5, len(event.tech_features or []))

def calculate_engagement_score(event: PatientJourneyEvent) -> int:
    engagement_factors = {
        JourneyStage.HESITANT: 1,
        JourneyStage.RESEARCHING: 2,
        JourneyStage.CONSULTING: 3,
        JourneyStage.ACCEPTING: 4,
        JourneyStage.COMPLETED: 5
    }
    return engagement_factors.get(event.journey_stage, 1)

def calculate_efficiency_score(event: PatientJourneyEvent) -> int:
    return min(5, int(event.metrics.get("process_efficiency", 1) * 5))

def calculate_practicality_score(event: PatientJourneyEvent) -> int:
    return min(5, int(event.metrics.get("business_value", 1) * 5))

def calculate_scalability_score(event: PatientJourneyEvent) -> int:
    return min(5, int(event.metrics.get("scalability_potential", 1) * 5))

def calculate_impact_score(event: PatientJourneyEvent) -> int:
    return min(5, int(event.metrics.get("impact_factor", 1) * 5))

@agent.on_interval(period=10.0)
async def analytics_report(ctx: Context):
    """Generate periodic analytics report every 10 seconds."""
    logging.info("\n=== Analytics Report ===")
    for patient_id, stats in analytics.journey_stats.items():
        logging.info(f"""
        Patient {patient_id} Statistics:
        - Stage Changes: {stats['stage_changes']}
        - Positive Sentiments: {stats['positive_sentiments']}
        - Negative Sentiments: {stats['negative_sentiments']}
        - Sentiment Ratio: {stats['positive_sentiments']/(stats['negative_sentiments'] + 1):.2f}
        """)

@agent.on_interval(period=10.0)
async def simulate_test_data(ctx: Context):
    """Simulate test patient data with metrics every 10 seconds."""
    test_event = PatientJourneyEvent(
        patient_id="TEST001",
        sentiment=Sentiment.POSITIVE,
        journey_stage=JourneyStage.RESEARCHING,
        timestamp=datetime.now(),
        notes="Test patient data with metrics",
        metrics={
            "process_efficiency": 0.8,
            "business_value": 0.9,
            "scalability_potential": 0.7,
            "impact_factor": 0.85
        },
        tech_features=["AI", "Blockchain", "API"]
    )
    logging.info("Simulating test patient data...")
    await ctx.send(agent.address, test_event)

agent.include(protocol)
print(analytics.journey_stats)
print(analytics.sentiment_history)
