from enum import Enum
from typing import Dict, Any

class EmotionType(str, Enum):
    HAPPY = "Happy"
    SAD = "Sad"
    ANGRY = "Angry"
    CURIOUS = "Curious"
    EXCITED = "Excited"
    AFRAID = "Afraid"
    LONELY = "Lonely"
    RELAXED = "Relaxed"
    FRUSTRATED = "Frustrated"

class EmotionalState:
    def __init__(self, initial_emotion: EmotionType = EmotionType.RELAXED):
        self.current_emotion: EmotionType = initial_emotion
        self.valence: float = 0.5   # -1.0 (unpleasant) to 1.0 (pleasant)
        self.arousal: float = 0.3   # 0.0 (calm) to 1.0 (activated)
        self.intensity: float = 0.5 # 0.0 to 1.0

    def update_from_needs(self, needs_dict: Dict[str, float]):
        """Evaluate emotional response to internal states."""
        hunger = needs_dict.get("hunger", 100.0)
        energy = needs_dict.get("energy", 100.0)
        social = needs_dict.get("social", 100.0)

        if hunger < 20.0 or energy < 15.0:
            self.set_emotion(EmotionType.FRUSTRATED, intensity=0.7)
        elif social < 25.0:
            self.set_emotion(EmotionType.LONELY, intensity=0.6)
        elif hunger > 75.0 and energy > 70.0 and social > 60.0:
            if self.current_emotion in (EmotionType.FRUSTRATED, EmotionType.LONELY):
                self.set_emotion(EmotionType.RELAXED, intensity=0.5)

    def set_emotion(self, emotion: EmotionType, intensity: float = 0.6):
        self.current_emotion = emotion
        self.intensity = max(0.0, min(1.0, intensity))
        
        # Adjust valence & arousal according to emotion type
        if emotion == EmotionType.HAPPY:
            self.valence = 0.8
            self.arousal = 0.5
        elif emotion == EmotionType.EXCITED:
            self.valence = 0.9
            self.arousal = 0.8
        elif emotion == EmotionType.RELAXED:
            self.valence = 0.6
            self.arousal = 0.2
        elif emotion == EmotionType.CURIOUS:
            self.valence = 0.5
            self.arousal = 0.6
        elif emotion == EmotionType.SAD:
            self.valence = -0.7
            self.arousal = 0.2
        elif emotion == EmotionType.LONELY:
            self.valence = -0.6
            self.arousal = 0.3
        elif emotion == EmotionType.FRUSTRATED:
            self.valence = -0.5
            self.arousal = 0.7
        elif emotion == EmotionType.ANGRY:
            self.valence = -0.8
            self.arousal = 0.9
        elif emotion == EmotionType.AFRAID:
            self.valence = -0.8
            self.arousal = 0.8

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current": self.current_emotion.value,
            "valence": round(self.valence, 2),
            "arousal": round(self.arousal, 2),
            "intensity": round(self.intensity, 2)
        }

