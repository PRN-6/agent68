from typing import Dict, Any, List, Optional
from app.ai.provider import LLMProvider, DailyPlan, PlanStep, DecisionOutput, DialogueTurnOutput, ReflectionOutput
from app.core.actions import SimulationAction, ActionType

class DeterministicMockProvider(LLMProvider):
    """Rich, deterministic mock AI provider for offline execution and automated test suites.
    Produces high-fidelity, context-aware plans, reflections, and dialogue based on NPC personality,
    needs, and social memory without needing external network calls.
    """

    async def generate_daily_plan(
        self,
        npc_data: Dict[str, Any],
        date_str: str,
        current_needs: Dict[str, float]
    ) -> DailyPlan:
        occ = npc_data.get("occupation", "Town Inhabitant").lower()
        home = npc_data.get("home_id", "home_1")
        work = npc_data.get("workplace_id", "town_square")
        name = npc_data.get("name", "Inhabitant")

        steps = [
            PlanStep(start_hour=0, start_minute=0, duration_minutes=420, activity="Night rest and sleep", location=home, description="Restful sleep at home."),
            PlanStep(start_hour=7, start_minute=0, duration_minutes=60, activity="Morning routine and breakfast", location=home, description="Wake up, stretch, and prepare a hearty breakfast."),
            PlanStep(start_hour=8, start_minute=0, duration_minutes=30, activity="Commute to work", location=work, description="Walk briskly towards the workplace, observing the town square."),
            PlanStep(start_hour=8, start_minute=30, duration_minutes=210, activity=f"Focus on {occ} duties", location=work, description=f"Perform daily professional work as a {occ}."),
            PlanStep(start_hour=12, start_minute=0, duration_minutes=60, activity="Lunch break and socialize", location="cafe" if occ != "baker" else "market", description="Enjoy a warm meal and greet fellow townspeople."),
            PlanStep(start_hour=13, start_minute=0, duration_minutes=240, activity="Afternoon responsibilities", location=work, description="Complete afternoon tasks and wrap up pending projects."),
            PlanStep(start_hour=17, start_minute=0, duration_minutes=90, activity="Evening stroll or visit tavern", location="pub", description="Unwind with colleagues, drink cider, and catch up on town news."),
            PlanStep(start_hour=18, start_minute=30, duration_minutes=90, activity="Dinner and personal hobbies", location=home, description="Cook evening dinner, read, and reflect on the day."),
            PlanStep(start_hour=20, start_minute=0, duration_minutes=120, activity="Evening relaxation and reading", location=home, description="Relax at home with a good book and tea."),
            PlanStep(start_hour=22, start_minute=0, duration_minutes=120, activity="Night rest and sleep", location=home, description="Head to bed for full restorative sleep.")
        ]

        summary = f"{name}'s daily routine: morning preparation at {home}, core {occ} duties at {work}, midday social lunch, and evening relaxation."
        return DailyPlan(date=date_str, summary=summary, steps=steps)

    async def decide_next_action(
        self,
        npc_data: Dict[str, Any],
        current_situation: Dict[str, Any],
        current_plan_step: Optional[Dict[str, Any]],
        needs: Dict[str, float],
        emotion: str,
        recent_memories: List[Dict[str, Any]],
        nearby_npcs: List[Dict[str, Any]]
    ) -> DecisionOutput:
        home = npc_data.get("home_id", "home_1")
        work = npc_data.get("workplace_id", "town_square")
        current_loc = npc_data.get("current_location", home)

        # 1. Critical Need Overrides
        if needs.get("hunger", 100.0) < 20.0:
            target = "cafe" if current_loc != "cafe" else current_loc
            if current_loc != "cafe" and current_loc != home:
                return DecisionOutput(
                    thought="My stomach is growling loudly. I need to get food immediately.",
                    action=SimulationAction(action_type=ActionType.MOVE_TO, target_location="cafe", duration_minutes=25, description="Walking to cafe for food"),
                    emotion_update="Hungry"
                )
            else:
                return DecisionOutput(
                    thought="I am eating a warm meal to restore my energy.",
                    action=SimulationAction(action_type=ActionType.EAT, target_location=current_loc, duration_minutes=25, description="Eating a nourishing meal"),
                    emotion_update="Content"
                )

        if needs.get("energy", 100.0) < 15.0:
            if current_loc != home:
                return DecisionOutput(
                    thought="Exhaustion is overwhelming me. I must return home to rest.",
                    action=SimulationAction(action_type=ActionType.MOVE_TO, target_location=home, duration_minutes=25, description="Returning home to sleep"),
                    emotion_update="Tired"
                )
            else:
                return DecisionOutput(
                    thought="Heading to bed to recover my energy.",
                    action=SimulationAction(action_type=ActionType.REST, target_location=home, duration_minutes=60, description="Deep restful sleep"),
                    emotion_update="Relaxed"
                )

        # 2. Social Opportunity if someone is nearby
        # Prompt conversation if social need is low, or feeling lonely, or at current location / free time
        is_social_urgent = needs.get("social", 100.0) < 50.0 or emotion == "Lonely"
        needs_travel = current_plan_step is not None and current_loc != current_plan_step.get("location", work)
        
        # Converse if someone is nearby AND (we don't need to commute elsewhere OR social need is urgent)
        if nearby_npcs and (is_social_urgent or not needs_travel or current_plan_step is None):
            target_npc = nearby_npcs[0]
            target_id = target_npc.get("id")
            target_name = target_npc.get("name", "fellow townsfolk")
            return DecisionOutput(
                thought=f"I see {target_name} nearby. A conversation would be pleasant.",
                action=SimulationAction(
                    action_type=ActionType.CONVERSE,
                    target_npc_id=target_id,
                    duration_minutes=15,
                    description=f"Starting a conversation with {target_name}"
                ),
                emotion_update="Curious"
            )

        # 3. Follow Plan Step (Primary Schedule Driver)
        if current_plan_step:
            target_loc = current_plan_step.get("location", work)
            activity = current_plan_step.get("activity", "Work")
            if current_loc != target_loc:
                return DecisionOutput(
                    thought=f"According to my schedule, I should be at {target_loc} for {activity}.",
                    action=SimulationAction(action_type=ActionType.MOVE_TO, target_location=target_loc, duration_minutes=25, description=f"Traveling to {target_loc}"),
                    emotion_update="Focused"
                )
            else:
                act_lower = activity.lower()
                # In the right place, do the scheduled activity
                if "work" in act_lower or "duties" in act_lower or "responsibilities" in act_lower:
                    act_type = ActionType.WORK
                elif "rest" in act_lower or "sleep" in act_lower:
                    act_type = ActionType.REST
                elif "lunch" in act_lower or "breakfast" in act_lower or "dinner" in act_lower or "eat" in act_lower:
                    act_type = ActionType.EAT
                else:
                    act_type = ActionType.RELAX

                # Keep action chunks to responsive durations (25-30 mins) so agents don't freeze indefinitely
                chunk_duration = min(30, current_plan_step.get("duration_minutes", 30))
                return DecisionOutput(
                    thought=f"Executing planned activity: {activity}",
                    action=SimulationAction(
                        action_type=act_type,
                        target_location=current_loc,
                        duration_minutes=chunk_duration,
                        description=activity
                    ),
                    emotion_update="Relaxed"
                )

        # Default fallback
        return DecisionOutput(
            thought="Taking a calm stroll around the area.",
            action=SimulationAction(action_type=ActionType.RELAX, target_location=current_loc, duration_minutes=20, description="Relaxing and enjoying the day"),
            emotion_update="Relaxed"
        )

    async def generate_dialogue_turn(
        self,
        speaker_data: Dict[str, Any],
        listener_data: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        topic: str,
        relationship_data: Dict[str, Any]
    ) -> DialogueTurnOutput:
        speaker_name = speaker_data.get("name", "Speaker")
        listener_name = listener_data.get("name", "Friend")
        speaker_occ = speaker_data.get("occupation", "inhabitant")
        turn_count = len(conversation_history)

        familiarity = relationship_data.get("familiarity", 10.0)

        # Turn 0: Greeting
        if turn_count == 0:
            if familiarity > 50.0:
                msg = f"Good day, {listener_name}! It is wonderful to run into you today. How are things with you?"
            else:
                msg = f"Hello there, {listener_name}. Beautiful day in town, wouldn't you say?"
            return DialogueTurnOutput(thought=f"Warmly greet {listener_name}", utterance=msg, sentiment=0.6)

        # Turn 1-2: Middle discussion
        elif turn_count < 4:
            prev_msg = conversation_history[-1].get("message", "")
            if "business" in topic.lower() or "work" in topic.lower():
                msg = f"Speaking of that, my work as {speaker_occ} has been quite busy lately. We should make sure the town square remains prosperous."
            elif "weather" in topic.lower():
                msg = "Indeed, the clear weather makes everything so much more pleasant around the plaza."
            else:
                msg = f"I appreciate your perspective, {listener_name}. It's always enlightening hearing how you see things in our community."
            return DialogueTurnOutput(thought="Engage meaningfully with their point", utterance=msg, sentiment=0.5)

        # Turn 4+: Farewell
        else:
            msg = f"Well, I must get back to my duties, {listener_name}. Let's catch up again soon! Take care."
            return DialogueTurnOutput(thought="Politely conclude the conversation", utterance=msg, end_conversation=True, sentiment=0.7)

    async def generate_reflection(
        self,
        npc_data: Dict[str, Any],
        memories: List[Dict[str, Any]]
    ) -> ReflectionOutput:
        name = npc_data.get("name", "Agent")
        occ = npc_data.get("occupation", "Citizen")
        
        supporting_ids = [m.get("id") for m in memories if m.get("id")]
        
        # Synthesize patterns
        insights = [
            f"{name} notices consistent cooperation and warmth among fellow town residents.",
            f"Balancing {occ} responsibilities with daily social life creates a sense of belonging in the community."
        ]
        new_beliefs = [
            "Active participation in town life fosters mutual trust and goodwill.",
            "Maintaining regular daily routines supports personal well-being."
        ]
        
        return ReflectionOutput(
            insights=insights,
            new_beliefs=new_beliefs,
            supporting_memory_ids=supporting_ids[:5]
        )

    async def replan_on_event(
        self,
        npc_data: Dict[str, Any],
        current_plan: List[Dict[str, Any]],
        event_description: str,
        current_needs: Dict[str, float]
    ) -> DailyPlan:
        name = npc_data.get("name", "Inhabitant")
        home = npc_data.get("home_id", "home_1")
        
        # Modify schedule to investigate or respond to event
        new_steps = []
        for step in current_plan:
            new_steps.append(PlanStep(
                start_hour=step.get("start_hour", 8),
                start_minute=step.get("start_minute", 0),
                duration_minutes=step.get("duration_minutes", 60),
                activity=step.get("activity", "Activity"),
                location=step.get("location", home),
                description=step.get("description", "")
            ))
            
        # Insert event response
        new_steps.insert(1, PlanStep(
            start_hour=9,
            start_minute=0,
            duration_minutes=60,
            activity=f"Investigate {event_description[:30]}...",
            location="town_square",
            description=f"Gather information regarding: {event_description}"
        ))
        
        return DailyPlan(
            date="Today (Updated)",
            summary=f"{name} altered plans to address: {event_description}",
            steps=new_steps
        )

