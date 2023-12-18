from enum import Enum
from typing import Any, Type, TYPE_CHECKING
from pydantic import BaseModel, Field

from metagpt.actions import Action, ActionOutput
from metagpt.actions.action_node import ActionNode
from metagpt.llm import LLM, HumanProvider
from metagpt.logs import logger
from metagpt.memory import Memory
from metagpt.schema import Message, MessageQueue
from metagpt.utils.common import any_to_str
from metagpt.utils.repair_llm_raw_output import extract_state_value_from_output

class RoleReactMode(str, Enum):
    REACT = "react"
    BY_ORDER = "by_order"
    PLAN_AND_ACT = "plan_and_act"

    @classmethod
    def values(cls):
        return [item.value for item in cls]


class RoleContextBase(BaseModel):
    env: "Environment" = None 
    msg_buffer: MessageQueue = Field(default_factory=MessageQueue) 
    memory: Memory = Field(default_factory=Memory) 
    state: int = Field(default=-1)
    todo: Action = Field(default=None) 
    react_mode: RoleReactMode = RoleReactMode.REACT
    max_react_loop: int = 1
    
if TYPE_CHECKING:
    from .environment import Environment