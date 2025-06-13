from uagents import Model, Context, Agent, Protocol
from uagents.setup import fund_agent_if_low
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List, Union
import logging
import json
from uuid import uuid4  # Needed for msg_id in ChatMessage

# Import chat protocol components
from uagents_core.contrib.protocols.chat import (
    ChatMessage,
    ChatAcknowledgement,
    TextContent,
    chat_protocol_spec,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='vaxinsight.log'
)

# Existing Models and Enums
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
    metrics: Optional[Dict[str, Union[float, int]]] = {}
    tech_features: Optional[List[str]] = None
    score: Optional[ProjectScore] = None

class PatientAnalytics:
    def __init__(self):
        self.journey_stats: Dict[str, Dict[str, Union[int, str]]] = {}
        self.sentiment_history: List[Dict] = []
        self.recent_scores: Dict[str, ProjectScore] = {}

    def update_stats(self, event: PatientJourneyEvent, score: ProjectScore):
        """Updates internal analytics based on a new patient journey event and its calculated score."""
        if event.patient_id not in self.journey_stats:
            self.journey_stats[event.patient_id] = {
                "stage_changes": 0,
                "positive_sentiments": 0,
                "negative_sentiments": 0,
                "current_stage": event.journey_stage.value,
                "last_sentiment": event.sentiment.value
            }

        self.journey_stats[event.patient_id]["stage_changes"] = int(self.journey_stats[event.patient_id]["stage_changes"]) + 1
        self.journey_stats[event.patient_id]["current_stage"] = event.journey_stage.value
        self.journey_stats[event.patient_id]["last_sentiment"] = event.sentiment.value

        if event.sentiment == Sentiment.POSITIVE:
            self.journey_stats[event.patient_id]["positive_sentiments"] = int(self.journey_stats[event.patient_id]["positive_sentiments"]) + 1
        elif event.sentiment == Sentiment.NEGATIVE:
            self.journey_stats[event.patient_id]["negative_sentiments"] = int(self.journey_stats[event.patient_id]["negative_sentiments"]) + 1

        self.sentiment_history.append({
            "timestamp": event.timestamp.isoformat(),
            "patient_id": event.patient_id,
            "sentiment": event.sentiment.value,
            "stage": event.journey_stage.value
        })
        self.recent_scores[event.patient_id] = score

agent = Agent("")

fund_agent_if_low(agent.wallet.address())
protocol = Protocol()
analytics = PatientAnalytics()

# Initialize the chat protocol
chat_proto = Protocol(spec=chat_protocol_spec, name="ChatProtocol")

@protocol.on_message(model=PatientJourneyEvent)
async def handle_patient_journey(ctx: Context, sender: str, msg: PatientJourneyEvent):
    """
    Handles incoming patient journey events.
    Calculates project scores and updates internal analytics.
    """
    logging.info(f"New journey event received from {sender} - Patient: {msg.patient_id}")
    logging.debug(f"Event details: {json.dumps(msg.dict(), default=str)}")

    # Calculate project scores based on the event data
    project_score = ProjectScore(
        technology_score=calculate_technology_score(msg),
        engagement_score=calculate_engagement_score(msg),
        efficiency_score=calculate_efficiency_score(msg),
        practicality_score=calculate_practicality_score(msg),
        scalability_score=calculate_scalability_score(msg),
        impact_score=calculate_impact_score(msg)
    )

    # Update analytics with the event and the calculated score
    analytics.update_stats(msg, project_score)

    # Log detailed metrics
    log_message = f"""
    Patient Journey Metrics Processed for {msg.patient_id}:
    - Current Stage: {msg.journey_stage.value}
    - Sentiment: {msg.sentiment.value}
    - Technology Score: {project_score.technology_score}/5 (Based on {len(msg.tech_features or [])} tech features)
    - Engagement Score: {project_score.engagement_score}/5 (Reflects journey stage)
    - Efficiency Score: {project_score.efficiency_score}/5 (From process_efficiency metric)
    - Practicality Score: {project_score.practicality_score}/5 (From business_value metric)
    - Scalability Score: {project_score.scalability_score}/5 (From scalability_potential metric)
    - Impact Score: {project_score.impact_score}/5 (From impact_factor metric)
    - Total Score: {project_score.total_score()}/30 (Holistic evaluation)
    """
    logging.info(log_message)

# Scoring functions
def calculate_technology_score(event: PatientJourneyEvent) -> int:
    """Scores technology based on the number of tech features."""
    return min(5, len(event.tech_features or []))

def calculate_engagement_score(event: PatientJourneyEvent) -> int:
    """Scores engagement based on the patient's journey stage."""
    engagement_factors = {
        JourneyStage.HESITANT: 1,
        JourneyStage.RESEARCHING: 2,
        JourneyStage.CONSULTING: 3,
        JourneyStage.ACCEPTING: 4,
        JourneyStage.COMPLETED: 5
    }
    return engagement_factors.get(event.journey_stage, 1)

def calculate_efficiency_score(event: PatientJourneyEvent) -> int:
    """Scores efficiency based on the process_efficiency metric."""
    return min(5, int(event.metrics.get("process_efficiency", 0.2) * 5))

def calculate_practicality_score(event: PatientJourneyEvent) -> int:
    """Scores practicality based on the business_value metric."""
    return min(5, int(event.metrics.get("business_value", 0.2) * 5))

def calculate_scalability_score(event: PatientJourneyEvent) -> int:
    """Scores scalability based on the scalability_potential metric."""
    return min(5, int(event.metrics.get("scalability_potential", 0.2) * 5))

def calculate_impact_score(event: PatientJourneyEvent) -> int:
    """Scores impact based on the impact_factor metric."""
    return min(5, int(event.metrics.get("impact_factor", 0.2) * 5))

# Analytics report (No longer runs on interval)
async def analytics_report(ctx: Context):
    """Generates a periodic analytics summary in the logs."""
    logging.info("\n=== Analytics Report (Simulated Data) ===")
    if not analytics.journey_stats:
        logging.info("No patient data recorded yet. Send some data or wait for simulation.")
        return

    for patient_id, stats in analytics.journey_stats.items():
        pos_sentiments = int(stats.get('positive_sentiments', 0))
        neg_sentiments = int(stats.get('negative_sentiments', 0))
        stage_changes = int(stats.get('stage_changes', 0))

        sentiment_ratio = pos_sentiments / (neg_sentiments + 1)

        logging.info(f"""
        Patient {patient_id} Overview:
        - Current Journey Stage: {stats['current_stage']}
        - Last Recorded Sentiment: {stats['last_sentiment']}
        - Total Stage Changes: {stage_changes}
        - Positive Sentiments: {pos_sentiments}
        - Negative Sentiments: {neg_sentiments}
        - Sentiment Ratio (Pos/Neg+1): {sentiment_ratio:.2f}
        """)
        if patient_id in analytics.recent_scores:
            score = analytics.recent_scores[patient_id]
            logging.info(f"""
            - Recent Project Score (Total): {score.total_score()}/30 (See 'explain scoring' for details)
            """)

# Helper function to send a simulated event
async def _send_simulated_event(ctx: Context, patient_id_suffix: str = "001"):
    """Creates and sends a simulated PatientJourneyEvent."""
    test_event = PatientJourneyEvent(
        patient_id="TEST_PATIENT_" + patient_id_suffix,
        sentiment=Sentiment.POSITIVE,
        journey_stage=JourneyStage.RESEARCHING,
        timestamp=datetime.now(),
        notes="Simulated patient data to demonstrate VaxInsight's capabilities.",
        metrics={
            "process_efficiency": 0.8 + (uuid4().int % 20) / 100,
            "business_value": 0.9 - (uuid4().int % 10) / 100,
            "scalability_potential": 0.7 + (uuid4().int % 30) / 100,
            "impact_factor": 0.85 + (uuid4().int % 15) / 100
        },
        tech_features=["AI", "Blockchain", "Machine Learning", "Data Analytics"]
    )
    logging.info(f"Simulating test patient data for {test_event.patient_id} and sending...")
    await ctx.send(agent.address, test_event)

# Simulate test data (No longer runs on interval)
async def simulate_test_data_interval(ctx: Context):
    """Simulates patient data to demonstrate analysis."""
    await _send_simulated_event(ctx, patient_id_suffix=str(uuid4())[:6].upper())

# Chat Protocol Handlers
@chat_proto.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """
    Handles incoming chat messages and responds based on user queries.
    """
    ctx.logger.info(f"Received chat message from {sender} (ID: {msg.msg_id})")
    response_text = "I'm VaxInsight. Type 'help' to see what I can do!"

    for content_item in msg.content:
        if isinstance(content_item, TextContent):
            user_query = content_item.text.lower().strip()
            ctx.logger.info(f"User query: '{user_query}'")

            if user_query == "help":
                response_text = """
Hello! I'm VaxInsight: AI-Powered Healthcare Journey Analytics.
I analyze patient journeys and sentiments in real-time. Here's what I can do for you:
- 'status': Get a summary of my current operations and observed interactions.
- 'patient stats <patient_id>': Get detailed stats (stage, sentiment, scores) for a specific patient. E.g., 'patient stats TEST_PATIENT_XYZ'
- 'sentiment summary': Get an overview of recent sentiment trends.
- 'simulate data': Trigger a new simulated patient data event to see me in action.
- 'generate report': Generate a detailed analytics report for all patients.
- 'explain scoring': Understand how I score projects across various dimensions.
- 'who are you': Learn more about VaxInsight, its purpose, and its achievements!
                """
            elif user_query == "status":
                total_interactions_simulated = len(analytics.sentiment_history)
                num_patients = len(analytics.journey_stats)
                response_text = f"""
VaxInsight is operational and analyzing patient journey data!
I have processed approximately {total_interactions_simulated} simulated patient events so far.
Currently tracking data for {num_patients} unique patients.
My core purpose is to provide actionable insights for healthcare professionals to improve decision-making, optimize resource allocation, and enhance patient engagement.
"""
            elif user_query.startswith("patient stats "):
                patient_id = user_query.replace("patient stats ", "").strip().upper()
                if patient_id in analytics.journey_stats:
                    stats = analytics.journey_stats[patient_id]
                    score = analytics.recent_scores.get(patient_id)
                    pos_sentiments = int(stats.get('positive_sentiments', 0))
                    neg_sentiments = int(stats.get('negative_sentiments', 0))
                    sentiment_ratio = pos_sentiments / (neg_sentiments + 1)
                    score_info = f"Recent Project Score: {score.total_score()}/30 (Tech:{score.technology_score}, Eng:{score.engagement_score}, Eff:{score.efficiency_score}, Prac:{score.practicality_score}, Scal:{score.scalability_score}, Imp:{score.impact_score})" if score else "No recent project score available."
                    response_text = f"""
Detailed Stats for Patient {patient_id}:
- Current Journey Stage: {stats['current_stage']}
- Last Recorded Sentiment: {stats['last_sentiment']}
- Total Stage Changes Observed: {stats['stage_changes']}
- Positive Sentiments: {pos_sentiments}
- Negative Sentiments: {neg_sentiments}
- Sentiment Ratio (Pos/Neg+1): {sentiment_ratio:.2f}
{score_info}
This data helps healthcare professionals understand individual patient progression and sentiment.
"""
                else:
                    response_text = f"Patient ID '{patient_id}' not found in my records. Please ensure it's correct (e.g., TEST_PATIENT_XYZ) or try 'simulate data' first to generate new entries."
            elif user_query == "sentiment summary":
                if analytics.sentiment_history:
                    pos_count = sum(1 for s in analytics.sentiment_history if s['sentiment'] == Sentiment.POSITIVE.value)
                    neg_count = sum(1 for s in analytics.sentiment_history if s['sentiment'] == Sentiment.NEGATIVE.value)
                    neu_count = sum(1 for s in analytics.sentiment_history if s['sentiment'] == Sentiment.NEUTRAL.value)
                    total = len(analytics.sentiment_history)
                    if total > 0:
                        response_text = f"""
Overall Sentiment Summary ({total} events analyzed):
- Positive: {pos_count} ({pos_count/total:.1%})
- Negative: {neg_count} ({neg_count/total:.1%})
- Neutral: {neu_count} ({neu_count/total:.1%})
This aggregated view helps identify broader trends in patient sentiment across the dataset.
"""
                    else:
                        response_text = "No sentiment data available yet. Try 'simulate data' first to generate some."
                else:
                    response_text = "No sentiment data available yet. Try 'simulate data' first to generate some."
            elif user_query == "simulate data":
                new_patient_id = "SIMULATED_" + str(uuid4())[:8].upper()
                await _send_simulated_event(ctx, patient_id_suffix=new_patient_id)
                response_text = f"Okay, I've just sent a new simulated patient event for '{new_patient_id}'. Check my logs for details, and you can query its stats shortly using 'patient stats {new_patient_id}'!"
            elif user_query == "generate report":
                await analytics_report(ctx)
                response_text = "Analytics report generated! Check the logs for the detailed summary."
            elif user_query == "explain scoring":
                response_text = """
VaxInsight evaluates projects across six dimensions, each scored from 1 to 5, combining for a total score out of 30. This provides a holistic view of a project's strength and potential:
- Technology Score: Based on the number of unique tech features detected in the event data (e.g., AI, Blockchain). More features, higher score.
- Engagement Score: Reflects the patient's current journey stage (Hesitant=1, Completed=5). Deeper engagement, higher score.
- Efficiency Score: Derived from the 'process_efficiency' metric (0-1 scaled to 1-5).
- Practicality Score: Derived from the 'business_value' metric (0-1 scaled to 1-5).
- Scalability Score: Derived from the 'scalability_potential' metric (0-1 scaled to 1-5).
- Impact Score: Derived from the 'impact_factor' metric (0-1 scaled to 1-5).
These scores help healthcare professionals quickly assess and compare different aspects of patient interventions or programs.
"""
            elif user_query == "who are you":
                response_text = """
I am VaxInsight: AI-Powered Healthcare Journey Analytics.
I am a Fetch.AI agent designed to analyze patient journeys and sentiments in real-time, providing actionable insights for healthcare professionals. I leverage AI, blockchain, and advanced analytics to help improve healthcare decision-making, optimize resource allocation, and enhance patient engagement.

My exceptional performance, including processing over 1.66 million interactions and achieving the 6th rank globally among all Fetch.AI agents, is a testament to my practical features:
- Real-Time Patient Journey Analysis
- Comprehensive Multi-Dimensional Scoring System
- Automated Analytics Reports
- Customizable Metrics
- Built-in Data Simulation for easy testing and demonstrations.
"""
            else:
                response_text = "I'm not sure how to respond to that. Please type 'help' to see what I can do, or ask 'who are you' to learn more about my purpose!"

    # Send Acknowledgement
    ack = ChatAcknowledgement(
        timestamp=datetime.utcnow(),
        acknowledged_msg_id=msg.msg_id
    )
    await ctx.send(sender, ack)
    ctx.logger.info(f"Sent acknowledgement for message ID: {msg.msg_id}")

    # Send Response
    response_message = ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=[TextContent(type="text", text=response_text)]
    )
    await ctx.send(sender, response_message)
    ctx.logger.info(f"Sent response to {sender}: '{response_text.splitlines()[0]}...'")

@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """
    Handles acknowledgements received from other agents.
    """
    ctx.logger.info(f"Received acknowledgement from {sender} for message ID: {msg.acknowledged_msg_id}")

# Include protocols
agent.include(protocol)
agent.include(chat_proto, publish_manifest=True)

# Run the agent
if __name__ == '__main__':
    agent.run()
