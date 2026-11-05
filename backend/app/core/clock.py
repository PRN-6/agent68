import asyncio
from datetime import datetime
from typing import Dict, Any

class SimulationClock:
    def __init__(self, start_hour: int = 7, start_minute: int = 0, start_day: int = 1):
        self.tick_count: int = 0
        self.sim_minute: int = start_minute
        self.sim_hour: int = start_hour
        self.sim_day: int = start_day
        self.is_running: bool = False
        self.speed_multiplier: float = 1.0  # 1x, 2x, 5x, 10x
        self.minutes_per_tick: int = 1
        self.last_tick_time: float = 0.0

    @property
    def total_sim_minutes(self) -> int:
        return (self.sim_day - 1) * 24 * 60 + self.sim_hour * 60 + self.sim_minute

    @property
    def formatted_time(self) -> str:
        return f"{self.sim_hour:02d}:{self.sim_minute:02d}"

    @property
    def day_phase(self) -> str:
        h = self.sim_hour
        if 5 <= h < 7:
            return "Dawn"
        elif 7 <= h < 12:
            return "Morning"
        elif 12 <= h < 17:
            return "Afternoon"
        elif 17 <= h < 21:
            return "Evening"
        else:
            return "Night"

    @property
    def is_daylight(self) -> bool:
        return 6 <= self.sim_hour < 20

    def tick(self) -> Dict[str, Any]:
        """Advance simulation clock by minutes_per_tick."""
        self.tick_count += 1
        self.sim_minute += self.minutes_per_tick
        
        day_rolled = False
        hour_rolled = False
        
        if self.sim_minute >= 60:
            hours_to_add = self.sim_minute // 60
            self.sim_minute = self.sim_minute % 60
            self.sim_hour += hours_to_add
            hour_rolled = True
            
            if self.sim_hour >= 24:
                days_to_add = self.sim_hour // 24
                self.sim_hour = self.sim_hour % 24
                self.sim_day += days_to_add
                day_rolled = True
                
        return {
            "tick": self.tick_count,
            "sim_day": self.sim_day,
            "sim_hour": self.sim_hour,
            "sim_minute": self.sim_minute,
            "formatted_time": self.formatted_time,
            "day_phase": self.day_phase,
            "is_daylight": self.is_daylight,
            "hour_rolled": hour_rolled,
            "day_rolled": day_rolled
        }

    def set_speed(self, multiplier: float):
        self.speed_multiplier = max(0.25, min(multiplier, 20.0))

    def pause(self):
        self.is_running = False

    def resume(self):
        self.is_running = True

    def reset(self, start_hour: int = 7, start_minute: int = 0, start_day: int = 1):
        self.tick_count = 0
        self.sim_minute = start_minute
        self.sim_hour = start_hour
        self.sim_day = start_day
        self.is_running = False

    def get_state(self) -> Dict[str, Any]:
        return {
            "tick": self.tick_count,
            "sim_day": self.sim_day,
            "sim_hour": self.sim_hour,
            "sim_minute": self.sim_minute,
            "formatted_time": self.formatted_time,
            "day_phase": self.day_phase,
            "is_daylight": self.is_daylight,
            "is_running": self.is_running,
            "speed": self.speed_multiplier,
            "total_sim_minutes": self.total_sim_minutes
        }
