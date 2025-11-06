"""
Journey Orchestration Models
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timedelta
from enum import Enum

class JourneyStepType(str, Enum):
    """Types of journey steps"""
    AGENT_ACTION = "agent_action"  # Agent analyzes and executes
    WAIT = "wait"  # Wait for time or event
    BRANCH = "branch"  # Conditional branching
    ENTRY = "entry"  # Entry point
    EXIT = "exit"  # Exit point

class WaitCondition(str, Enum):
    """Wait conditions"""
    TIME = "time"  # Wait for duration
    EVENT = "event"  # Wait for event (email opened, etc.)
    BOTH = "both"  # Wait for time OR event

class JourneyStep(BaseModel):
    """A single step in a journey"""
    step_id: str
    step_type: JourneyStepType
    name: str
    description: Optional[str] = None
    
    # For agent_action steps
    agent_instructions: Optional[str] = None
    channels: Optional[List[str]] = None
    
    # For wait steps
    wait_condition: Optional[WaitCondition] = None
    wait_duration_hours: Optional[int] = None
    wait_event_type: Optional[str] = None  # e.g., "email_opened", "conversion"
    
    # For branch steps
    branch_conditions: Optional[List[Dict[str, Any]]] = None  # [{condition: "opened", next_step: "step_2"}, ...]
    
    # Execution
    next_step_id: Optional[str] = None  # Default next step
    exit_on_error: bool = False

class JourneyDefinition(BaseModel):
    """Complete journey definition"""
    journey_id: str
    tenant_id: str
    name: str
    description: Optional[str] = None
    
    # Entry conditions
    entry_trigger: str  # "segment", "event", "manual"
    entry_segment: Optional[str] = None
    entry_event_type: Optional[str] = None
    
    # Steps
    steps: List[JourneyStep]
    entry_step_id: str  # First step to execute
    
    # Configuration
    agent_model: Optional[str] = None
    max_duration_days: Optional[int] = None
    
    # Status
    status: str = "draft"  # draft, active, paused, archived
    
    # Metadata
    created_by: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class JourneyDefinitionCreate(BaseModel):
    """Request model for creating a journey"""
    name: str
    description: Optional[str] = None
    entry_trigger: str
    entry_segment: Optional[str] = None
    entry_event_type: Optional[str] = None
    steps: List[JourneyStep]
    entry_step_id: str
    agent_model: Optional[str] = None
    max_duration_days: Optional[int] = None

class JourneyDefinitionUpdate(BaseModel):
    """Request model for updating a journey"""
    name: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[List[JourneyStep]] = None
    entry_step_id: Optional[str] = None
    status: Optional[str] = None
    max_duration_days: Optional[int] = None

class CustomerJourneyState(BaseModel):
    """State of a customer in a journey"""
    state_id: str
    tenant_id: str
    customer_id: str
    journey_id: str
    
    current_step_id: str
    status: str  # active, waiting, completed, exited, error
    
    # Wait state
    waiting_for: Optional[str] = None  # "time", "event", "both"
    wait_until: Optional[datetime] = None
    
    # Progress tracking
    steps_completed: List[str] = []
    actions_taken: List[Dict[str, Any]] = []  # History of actions
    
    # Timing
    entered_at: datetime
    last_action_at: datetime
    completed_at: Optional[datetime] = None
    exit_reason: Optional[str] = None
    
    class Config:
        from_attributes = True

class JourneyExecutionRequest(BaseModel):
    """Request to execute a journey for customers"""
    journey_id: str
    customer_ids: Optional[List[str]] = None  # If None, uses entry trigger
    segment: Optional[str] = None

class JourneyProgressResponse(BaseModel):
    """Response showing journey progress"""
    journey_id: str
    journey_name: str
    total_entered: int
    active_states: int
    waiting_states: int
    completed_states: int
    exited_states: int
    step_breakdown: Dict[str, Dict[str, int]]  # {step_id: {entered: X, completed: Y}}

