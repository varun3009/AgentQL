from enum import Enum

class LLMStatus(Enum):
    INTERRUPT = 1
    COMPLETED = 2

class Role(Enum):
    HUMAN = 1
    AGENT = 2