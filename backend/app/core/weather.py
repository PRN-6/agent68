import random
from typing import Dict, Any

class WeatherSystem:
    WEATHER_TYPES = [
        {"type": "Sunny", "description": "Clear skies with golden sunshine.", "comfort_mod": 1.1, "is_rain": False},
        {"type": "Partly Cloudy", "description": "Gentle breeze with drifting clouds.", "comfort_mod": 1.0, "is_rain": False},
        {"type": "Gentle Rain", "description": "A soft, peaceful rain falling over town.", "comfort_mod": 0.85, "is_rain": True},
        {"type": "Windy", "description": "Brisk autumn winds rustling through the trees.", "comfort_mod": 0.9, "is_rain": False},
        {"type": "Thunderstorm", "description": "Rumbling thunder and heavy rain.", "comfort_mod": 0.7, "is_rain": True},
    ]

    def __init__(self):
        self.current_weather = self.WEATHER_TYPES[0]
        self.hours_until_change = random.randint(4, 8)
        self.temperature = 21.0  # Celsius

    def tick_hourly(self) -> Dict[str, Any]:
        self.hours_until_change -= 1
        if self.hours_until_change <= 0:
            # Change weather
            weights = [0.45, 0.30, 0.15, 0.07, 0.03]
            self.current_weather = random.choices(self.WEATHER_TYPES, weights=weights)[0]
            self.hours_until_change = random.randint(4, 9)
            
            # Adjust temperature
            if self.current_weather["is_rain"]:
                self.temperature = round(random.uniform(15.0, 19.0), 1)
            else:
                self.temperature = round(random.uniform(20.0, 26.0), 1)
                
        return self.get_state()

    def get_state(self) -> Dict[str, Any]:
        return {
            "type": self.current_weather["type"],
            "description": self.current_weather["description"],
            "comfort_mod": self.current_weather["comfort_mod"],
            "is_rain": self.current_weather["is_rain"],
            "temperature": self.temperature
        }

