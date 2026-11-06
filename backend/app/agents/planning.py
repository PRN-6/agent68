from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.ai.provider import DailyPlan, PlanStep
from app.ai import get_ai_provider

class ScheduleItem(BaseModel):
    start_hour: int
    start_minute: int = 0
    duration_minutes: int
    activity: str
    location: str
    description: str
    is_completed: bool = False

    @property
    def end_minute_of_day(self) -> int:
        return self.start_hour * 60 + self.start_minute + self.duration_minutes

    @property
    def start_minute_of_day(self) -> int:
        return self.start_hour * 60 + self.start_minute

class Planner:
    def __init__(self, npc_id: str):
        self.npc_id = npc_id
        self.current_day: int = 0
        self.schedule: List[ScheduleItem] = []
        self.plan_summary: str = ""

    async def generate_schedule_for_day(
        self,
        npc_data: Dict[str, Any],
        sim_day: int,
        date_str: str,
        current_needs: Dict[str, float]
    ):
        self.current_day = sim_day
        ai = get_ai_provider()
        plan: DailyPlan = await ai.generate_daily_plan(npc_data, date_str, current_needs)
        
        self.plan_summary = plan.summary
        self.schedule = [
            ScheduleItem(
                start_hour=s.start_hour,
                start_minute=s.start_minute,
                duration_minutes=s.duration_minutes,
                activity=s.activity,
                location=s.location,
                description=s.description
            )
            for s in plan.steps
        ]
        # Sort schedule chronologically
        self.schedule.sort(key=lambda s: s.start_minute_of_day)

    def get_current_step(self, sim_hour: int, sim_minute: int) -> Optional[ScheduleItem]:
        if not self.schedule:
            return None
        current_minute_of_day = (sim_hour % 24) * 60 + sim_minute
        for item in self.schedule:
            if item.start_minute_of_day <= current_minute_of_day < item.end_minute_of_day:
                return item
        # If between steps or end of day, find the closest active item
        for item in reversed(self.schedule):
            if current_minute_of_day >= item.start_minute_of_day:
                return item
        return self.schedule[0]

    async def handle_unexpected_event(
        self,
        npc_data: Dict[str, Any],
        event_description: str,
        current_needs: Dict[str, float]
    ):
        """Dynamic plan revision in response to external changes or urgent circumstances."""
        ai = get_ai_provider()
        updated_plan = await ai.replan_on_event(
            npc_data=npc_data,
            current_plan=[s.model_dump() for s in self.schedule],
            event_description=event_description,
            current_needs=current_needs
        )
        self.plan_summary = updated_plan.summary
        self.schedule = [
            ScheduleItem(
                start_hour=s.start_hour,
                start_minute=s.start_minute,
                duration_minutes=s.duration_minutes,
                activity=s.activity,
                location=s.location,
                description=s.description
            )
            for s in updated_plan.steps
        ]
        self.schedule.sort(key=lambda s: s.start_minute_of_day)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_day": self.current_day,
            "summary": self.plan_summary,
            "schedule": [s.model_dump() for s in self.schedule]
        }
