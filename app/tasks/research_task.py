from crewai import Task
from app.agents.researcher import create_researcher_agent

def create_research_task(topic: str) -> Task:
    researcher = create_researcher_agent()
    
    return Task(
        description=f"""Research and analyze the following topic: {topic}
        Provide a comprehensive analysis including:
        1. Key findings
        2. Important statistics
        3. Relevant trends
        4. Potential implications""",
        agent=researcher,
        expected_output="""A detailed research report containing:
        1. Executive summary
        2. Key findings and insights
        3. Statistical analysis
        4. Trend analysis
        5. Recommendations and implications
        6. Sources and references"""
    ) 