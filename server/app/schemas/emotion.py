from typing import List
from enum import Enum

class Emotion(Enum):
    # System states
    NOTICED = "noticed"
    PROGRESS = "progress"
    
    # Basic emotions
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SCARED = "scared"
    SURPRISED = "surprised"
    DISGUSTED = "disgusted"
    
    # Positive emotions
    EXCITED = "excited"
    JOYFUL = "joyful"
    PEACEFUL = "peaceful"
    GRATEFUL = "grateful"
    PROUD = "proud"
    CONFIDENT = "confident"
    AMUSED = "amused"
    LOVING = "loving"
    
    # Negative emotions
    ANXIOUS = "anxious"
    FRUSTRATED = "frustrated"
    DISAPPOINTED = "disappointed"
    EMBARRASSED = "embarrassed"
    GUILTY = "guilty"
    JEALOUS = "jealous"
    LONELY = "lonely"
    
    # Other emotional states
    NEUTRAL = "neutral"
    CONFUSED = "confused"
    CURIOUS = "curious"
    DETERMINED = "determined"
    TIRED = "tired"
    ENERGETIC = "energetic"
    HOPEFUL = "hopeful"
    NOSTALGIC = "nostalgic"
    SATISFIED = "satisfied"
    BORED = "bored"
    THOUGHTFUL = "thoughtful"
    ENTHUSIASTIC = "enthusiastic"
    RELAXED = "relaxed"
    IMPRESSED = "impressed"
    SKEPTICAL = "skeptical"
    
    @classmethod
    def to_request_values(cls) -> List[str]:
        return [e.value for e in cls]
