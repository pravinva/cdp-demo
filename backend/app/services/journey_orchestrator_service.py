"""
Journey Orchestrator Service
State machine that orchestrates multi-step customer journeys with agent integration
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from ..models.journey import (
    JourneyDefinition,
    JourneyDefinitionCreate,
    CustomerJourneyState,
    JourneyStep,
    JourneyStepType,
    WaitCondition
)
from ..dependencies import get_workspace_client
from ..config import get_settings
from .agent_service import AgentService

settings = get_settings()


class JourneyOrchestratorService:
    """
    Orchestrates customer journeys as a state machine
    
    Features:
    - Multi-step journey execution
    - Integration with Agent Service for decision-making
    - Wait conditions (time-based and event-based)
    - Conditional branching
    - State persistence in Delta Lake
    """
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.w = get_workspace_client()
        self.settings = get_settings()
        self.warehouse_id = self.settings.SQL_WAREHOUSE_ID or "4b9b953939869799"
        self.agent_service = AgentService(tenant_id)
    
    def create_journey(self, journey_def: JourneyDefinitionCreate, created_by: str) -> JourneyDefinition:
        """Create a new journey definition"""
        journey_id = f"journey_{uuid.uuid4().hex[:8]}"
        
        journey = JourneyDefinition(
            journey_id=journey_id,
            tenant_id=self.tenant_id,
            name=journey_def.name,
            description=journey_def.description,
            entry_trigger=journey_def.entry_trigger,
            entry_segment=journey_def.entry_segment,
            entry_event_type=journey_def.entry_event_type,
            steps=journey_def.steps,
            entry_step_id=journey_def.entry_step_id,
            agent_model=journey_def.agent_model,
            max_duration_days=journey_def.max_duration_days,
            status="draft",
            created_by=created_by,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Store in database
        definition_json = journey.model_dump_json().replace("'", "''")
        name = journey.name.replace("'", "''")
        description = (journey.description or "").replace("'", "''")
        
        insert_query = f"""
            INSERT INTO cdp_platform.core.journey_definitions
            (journey_id, tenant_id, name, description, definition_json, status, created_by, created_at, updated_at)
            VALUES (
                '{journey_id}',
                '{self.tenant_id}',
                '{name}',
                '{description}',
                '{definition_json}',
                'draft',
                '{created_by}',
                current_timestamp(),
                current_timestamp()
            )
        """
        
        try:
            self.w.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=insert_query,
                wait_timeout="30s"
            )
        except Exception as e:
            print(f"Error creating journey: {e}")
            raise
        
        return journey
    
    def get_journey(self, journey_id: str) -> Optional[JourneyDefinition]:
        """Retrieve a journey definition"""
        query = f"""
            SELECT definition_json
            FROM cdp_platform.core.journey_definitions
            WHERE tenant_id = '{self.tenant_id}' AND journey_id = '{journey_id}'
        """
        
        try:
            response = self.w.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=query,
                wait_timeout="30s"
            )
            
            if not response.result or not response.result.data_array:
                return None
            
            columns = [col.name for col in response.manifest.schema.columns] if response.manifest and response.manifest.schema else []
            definition_json = response.result.data_array[0][0]
            return JourneyDefinition.model_validate_json(definition_json)
        except Exception as e:
            print(f"Error getting journey: {e}")
            return None
    
    def update_journey(self, journey_id: str, updates: Dict[str, Any]) -> Optional[JourneyDefinition]:
        """Update a journey definition"""
        journey = self.get_journey(journey_id)
        if not journey:
            return None
        
        # Update fields
        if 'name' in updates:
            journey.name = updates['name']
        if 'description' in updates:
            journey.description = updates['description']
        if 'steps' in updates:
            journey.steps = updates['steps']
        if 'entry_step_id' in updates:
            journey.entry_step_id = updates['entry_step_id']
        if 'status' in updates:
            journey.status = updates['status']
        if 'max_duration_days' in updates:
            journey.max_duration_days = updates['max_duration_days']
        
        journey.updated_at = datetime.now()
        
        # Persist
        definition_json = journey.model_dump_json().replace("'", "''")
        update_query = f"""
            UPDATE cdp_platform.core.journey_definitions
            SET definition_json = '{definition_json}',
                updated_at = current_timestamp()
            WHERE tenant_id = '{self.tenant_id}' AND journey_id = '{journey_id}'
        """
        
        try:
            self.w.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=update_query,
                wait_timeout="30s"
            )
        except Exception as e:
            print(f"Error updating journey: {e}")
            raise
        
        return journey
    
    def activate_journey(self, journey_id: str) -> bool:
        """Activate a journey (change status to active)"""
        update_query = f"""
            UPDATE cdp_platform.core.journey_definitions
            SET status = 'active',
                updated_at = current_timestamp()
            WHERE tenant_id = '{self.tenant_id}' AND journey_id = '{journey_id}'
        """
        
        try:
            self.w.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=update_query,
                wait_timeout="30s"
            )
            return True
        except Exception as e:
            print(f"Error activating journey: {e}")
            return False
    
    def enter_customers_to_journey(
        self,
        journey_id: str,
        customer_ids: Optional[List[str]] = None,
        segment: Optional[str] = None
    ) -> int:
        """
        Enter customers into a journey
        
        If customer_ids provided, use those.
        If segment provided, find all customers in segment.
        Otherwise, use journey's entry_trigger.
        """
        journey = self.get_journey(journey_id)
        if not journey or journey.status != 'active':
            raise ValueError(f"Journey {journey_id} not found or not active")
        
        # Determine which customers to enter
        if customer_ids:
            customers_to_enter = customer_ids
        elif segment:
            query = f"""
                SELECT customer_id
                FROM cdp_platform.core.customers
                WHERE tenant_id = '{self.tenant_id}' AND segment = '{segment}'
            """
            customers_to_enter = []
            try:
                response = self.w.statement_execution.execute_statement(
                    warehouse_id=self.warehouse_id,
                    statement=query,
                    wait_timeout="30s"
                )
                if response.result and response.result.data_array:
                    customers_to_enter = [row[0] for row in response.result.data_array]
            except Exception as e:
                print(f"Error getting customers by segment: {e}")
        elif journey.entry_segment:
            query = f"""
                SELECT customer_id
                FROM cdp_platform.core.customers
                WHERE tenant_id = '{self.tenant_id}' AND segment = '{journey.entry_segment}'
            """
            customers_to_enter = []
            try:
                response = self.w.statement_execution.execute_statement(
                    warehouse_id=self.warehouse_id,
                    statement=query,
                    wait_timeout="30s"
                )
                if response.result and response.result.data_array:
                    customers_to_enter = [row[0] for row in response.result.data_array]
            except Exception as e:
                print(f"Error getting customers by entry_segment: {e}")
        else:
            raise ValueError("Must provide customer_ids or segment")
        
        # Create journey states
        states_to_insert = []
        now = datetime.now()
        
        for customer_id in customers_to_enter:
            state_id = f"state_{uuid.uuid4().hex}"
            states_to_insert.append({
                'state_id': state_id,
                'tenant_id': self.tenant_id,
                'customer_id': customer_id,
                'journey_id': journey_id,
                'current_step_id': journey.entry_step_id,
                'status': 'active',
                'waiting_for': None,
                'wait_until': None,
                'steps_completed': [],
                'actions_taken': '[]',
                'entered_at': now,
                'last_action_at': now,
                'completed_at': None,
                'exit_reason': None
            })
        
        # Bulk insert - insert one by one (SQL Execution API doesn't support bulk insert easily)
        if states_to_insert:
            for state in states_to_insert:
                steps_completed_json = json.dumps(state['steps_completed'])
                insert_query = f"""
                    INSERT INTO cdp_platform.core.customer_journey_states
                    (state_id, tenant_id, customer_id, journey_id, current_step_id, status,
                     waiting_for, wait_until, steps_completed, actions_taken,
                     entered_at, last_action_at, completed_at, exit_reason)
                    VALUES (
                        '{state['state_id']}',
                        '{state['tenant_id']}',
                        '{state['customer_id']}',
                        '{state['journey_id']}',
                        '{state['current_step_id']}',
                        '{state['status']}',
                        NULL,
                        NULL,
                        ARRAY({','.join([f"'{s}'" for s in state['steps_completed']])}),
                        '{state['actions_taken']}',
                        current_timestamp(),
                        current_timestamp(),
                        NULL,
                        NULL
                    )
                """
                try:
                    self.w.statement_execution.execute_statement(
                        warehouse_id=self.warehouse_id,
                        statement=insert_query,
                        wait_timeout="30s"
                    )
                except Exception as e:
                    print(f"Error inserting journey state: {e}")
        
        return len(states_to_insert)
    
    def process_journey_states(self) -> Dict[str, int]:
        """
        Process all active journey states
        Called periodically by background worker
        
        Returns counts of processed states
        """
        stats = {
            'agent_actions': 0,
            'waits_checked': 0,
            'branches_evaluated': 0,
            'completed': 0,
            'errors': 0
        }
        
        # Get all active states
        query = f"""
            SELECT state_id, customer_id, journey_id, current_step_id, status,
                   waiting_for, wait_until, steps_completed, actions_taken
            FROM cdp_platform.core.customer_journey_states
            WHERE tenant_id = '{self.tenant_id}'
            AND status IN ('active', 'waiting')
        """
        
        active_states = []
        try:
            response = self.w.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=query,
                wait_timeout="30s"
            )
            if response.result and response.result.data_array:
                columns = [col.name for col in response.manifest.schema.columns] if response.manifest and response.manifest.schema else []
                for row in response.result.data_array:
                    row_dict = {columns[i]: row[i] for i in range(len(columns))}
                    # Handle datetime conversion
                    if 'wait_until' in row_dict and row_dict['wait_until']:
                        if isinstance(row_dict['wait_until'], str):
                            try:
                                row_dict['wait_until'] = datetime.fromisoformat(row_dict['wait_until'].replace('Z', '+00:00'))
                            except:
                                pass
                    # Handle array conversion
                    if 'steps_completed' in row_dict and isinstance(row_dict['steps_completed'], str):
                        try:
                            row_dict['steps_completed'] = json.loads(row_dict['steps_completed'])
                        except:
                            row_dict['steps_completed'] = []
                    active_states.append(row_dict)
        except Exception as e:
            print(f"Error getting active states: {e}")
            return stats
        
        for state_row in active_states:
            try:
                journey = self.get_journey(state_row.get('journey_id'))
                if not journey:
                    continue
                
                step = self._find_step(journey, state_row.get('current_step_id'))
                if not step:
                    self._exit_journey(
                        state_row.get('state_id'),
                        "Invalid step_id"
                    )
                    stats['errors'] += 1
                    continue
                
                # Process based on step type
                if step.step_type == JourneyStepType.AGENT_ACTION:
                    stats['agent_actions'] += self._execute_agent_step(
                        state_row.get('state_id'),
                        state_row.get('customer_id'),
                        journey,
                        step
                    )
                
                elif step.step_type == JourneyStepType.WAIT:
                    stats['waits_checked'] += self._check_wait_step(
                        state_row.get('state_id'),
                        state_row.get('customer_id'),
                        journey,
                        step,
                        state_row.get('waiting_for'),
                        state_row.get('wait_until')
                    )
                
                elif step.step_type == JourneyStepType.BRANCH:
                    stats['branches_evaluated'] += self._evaluate_branch(
                        state_row.get('state_id'),
                        state_row.get('customer_id'),
                        journey,
                        step
                    )
                
                elif step.step_type == JourneyStepType.EXIT:
                    self._exit_journey(state_row.get('state_id'), "Journey completed")
                    stats['completed'] += 1
                
            except Exception as e:
                print(f"Error processing state {state_row.get('state_id')}: {e}")
                self._exit_journey(state_row.get('state_id'), f"Error: {str(e)}")
                stats['errors'] += 1
        
        return stats
    
    def _find_step(self, journey: JourneyDefinition, step_id: str) -> Optional[JourneyStep]:
        """Find a step by ID"""
        for step in journey.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def _execute_agent_step(
        self,
        state_id: str,
        customer_id: str,
        journey: JourneyDefinition,
        step: JourneyStep
    ) -> int:
        """
        Execute an agent action step
        Calls agent service to analyze customer and make decision
        """
        # Check if already executed (prevent duplicate execution)
        state = self._get_journey_state(state_id)
        if state and step.step_id in state['steps_completed']:
            # Already executed, move to next step
            if step.next_step_id:
                self._advance_to_step(state_id, step.next_step_id)
            return 0
        
        # Execute agent decision
        decision = self.agent_service.analyze_and_decide(
            customer_id=customer_id,
            campaign_id=None,  # Journey-based, not campaign
            journey_id=journey.journey_id,
            journey_step_id=step.step_id,
            agent_instructions=step.agent_instructions or journey.agent_model,
            channels=step.channels or ["email"]
        )
        
        # Record action
        action_record = {
            'step_id': step.step_id,
            'timestamp': datetime.now().isoformat(),
            'decision_id': decision.decision_id,
            'action': decision.action,
            'channel': decision.channel
        }
        
        self._add_action(state_id, action_record)
        self._mark_step_completed(state_id, step.step_id)
        
        # If agent decided to skip, exit journey
        if decision.action == 'skip':
            self._exit_journey(state_id, "Agent decided to skip")
            return 1
        
        # If agent decided to contact, delivery will be created
        # Move to next step (or wait step if configured)
        if step.next_step_id:
            self._advance_to_step(state_id, step.next_step_id)
        
        return 1
    
    def _check_wait_step(
        self,
        state_id: str,
        customer_id: str,
        journey: JourneyDefinition,
        step: JourneyStep,
        current_waiting_for: Optional[str],
        wait_until: Optional[datetime]
    ) -> int:
        """
        Check if wait condition is satisfied
        Returns 1 if checked, 0 if still waiting
        """
        if not current_waiting_for:
            # Initialize wait
            if step.wait_condition == WaitCondition.TIME:
                wait_hours = step.wait_duration_hours or 24
                wait_until_dt = datetime.now() + timedelta(hours=wait_hours)
                self._set_wait_state(state_id, "time", wait_until_dt)
                return 1
            
            elif step.wait_condition == WaitCondition.EVENT:
                self._set_wait_state(state_id, "event", None)
                # Event will be checked when delivery events come in
                return 1
            
            elif step.wait_condition == WaitCondition.BOTH:
                wait_hours = step.wait_duration_hours or 24
                wait_until_dt = datetime.now() + timedelta(hours=wait_hours)
                self._set_wait_state(state_id, "both", wait_until_dt)
                return 1
        
        # Check if wait is satisfied
        if step.wait_condition == WaitCondition.TIME:
            if wait_until and datetime.now() >= wait_until:
                # Wait satisfied, move to next step
                self._clear_wait_state(state_id)
                if step.next_step_id:
                    self._advance_to_step(state_id, step.next_step_id)
                return 1
        
        elif step.wait_condition == WaitCondition.EVENT:
            # Check if event occurred
            event_type = step.wait_event_type or "email_opened"
            if self._check_event_occurred(customer_id, journey.journey_id, event_type):
                self._clear_wait_state(state_id)
                if step.next_step_id:
                    self._advance_to_step(state_id, step.next_step_id)
                return 1
        
        elif step.wait_condition == WaitCondition.BOTH:
            # Check if time expired OR event occurred
            event_occurred = self._check_event_occurred(
                customer_id,
                journey.journey_id,
                step.wait_event_type or "email_opened"
            )
            
            if (wait_until and datetime.now() >= wait_until) or event_occurred:
                self._clear_wait_state(state_id)
                if step.next_step_id:
                    self._advance_to_step(state_id, step.next_step_id)
                return 1
        
        return 0
    
    def _evaluate_branch(
        self,
        state_id: str,
        customer_id: str,
        journey: JourneyDefinition,
        step: JourneyStep
    ) -> int:
        """
        Evaluate branch conditions and route to appropriate next step
        """
        if not step.branch_conditions:
            # No conditions, use default next_step
            if step.next_step_id:
                self._advance_to_step(state_id, step.next_step_id)
            return 1
        
        # Check each condition
        for condition in step.branch_conditions:
            condition_type = condition.get('condition')  # e.g., "opened", "clicked", "converted"
            
            if self._check_event_occurred(customer_id, journey.journey_id, condition_type):
                next_step = condition.get('next_step_id')
                if next_step:
                    self._advance_to_step(state_id, next_step)
                    return 1
        
        # No condition matched, use default next_step
        if step.next_step_id:
            self._advance_to_step(state_id, step.next_step_id)
        
        return 1
    
    def _check_event_occurred(
        self,
        customer_id: str,
        journey_id: str,
        event_type: str
    ) -> bool:
        """
        Check if a specific event occurred for this customer in this journey
        """
        # Map event types to delivery fields
        event_mapping = {
            'email_opened': ('opened', True),
            'email_clicked': ('clicked', True),
            'conversion': ('converted', True),
            'delivered': ('delivered', True)
        }
        
        if event_type not in event_mapping:
            return False
        
        field, value = event_mapping[event_type]
        
        # Check deliveries table
        query = f"""
            SELECT COUNT(*) as count
            FROM cdp_platform.core.deliveries d
            INNER JOIN cdp_platform.core.customer_journey_states cjs
                ON d.customer_id = cjs.customer_id AND d.journey_id = cjs.journey_id
            WHERE d.tenant_id = '{self.tenant_id}'
            AND d.customer_id = '{customer_id}'
            AND d.journey_id = '{journey_id}'
            AND d.{field} = {value}
        """
        
        try:
            response = self.w.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=query,
                wait_timeout="30s"
            )
            if response.result and response.result.data_array:
                count = int(response.result.data_array[0][0] or 0)
                return count > 0
        except Exception as e:
            print(f"Error checking event: {e}")
        
        return False
    
    def _advance_to_step(self, state_id: str, next_step_id: str):
        """Advance journey state to next step"""
        update_query = f"""
            UPDATE cdp_platform.core.customer_journey_states
            SET current_step_id = '{next_step_id}',
                status = 'active',
                last_action_at = current_timestamp()
            WHERE tenant_id = '{self.tenant_id}' AND state_id = '{state_id}'
        """
        
        try:
            self.w.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=update_query,
                wait_timeout="30s"
            )
        except Exception as e:
            print(f"Error advancing step: {e}")
    
    def _set_wait_state(self, state_id: str, waiting_for: str, wait_until: Optional[datetime]):
        """Set journey state to waiting"""
        wait_until_str = f"timestamp('{wait_until.isoformat()}')" if wait_until else "NULL"
        
        update_query = f"""
            UPDATE cdp_platform.core.customer_journey_states
            SET status = 'waiting',
                waiting_for = '{waiting_for}',
                wait_until = {wait_until_str},
                last_action_at = current_timestamp()
            WHERE tenant_id = '{self.tenant_id}' AND state_id = '{state_id}'
        """
        
        try:
            self.w.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=update_query,
                wait_timeout="30s"
            )
        except Exception as e:
            print(f"Error setting wait state: {e}")
    
    def _clear_wait_state(self, state_id: str):
        """Clear wait state"""
        update_query = f"""
            UPDATE cdp_platform.core.customer_journey_states
            SET status = 'active',
                waiting_for = NULL,
                wait_until = NULL,
                last_action_at = current_timestamp()
            WHERE tenant_id = '{self.tenant_id}' AND state_id = '{state_id}'
        """
        
        try:
            self.w.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=update_query,
                wait_timeout="30s"
            )
        except Exception as e:
            print(f"Error clearing wait state: {e}")
    
    def _mark_step_completed(self, state_id: str, step_id: str):
        """Mark a step as completed"""
        state = self._get_journey_state(state_id)
        if state:
            completed_steps = state.get('steps_completed', [])
            if isinstance(completed_steps, str):
                try:
                    completed_steps = json.loads(completed_steps)
                except:
                    completed_steps = []
            if step_id not in completed_steps:
                completed_steps.append(step_id)
                update_query = f"""
                    UPDATE cdp_platform.core.customer_journey_states
                    SET steps_completed = ARRAY({','.join([f"'{s}'" for s in completed_steps])}),
                        last_action_at = current_timestamp()
                    WHERE tenant_id = '{self.tenant_id}' AND state_id = '{state_id}'
                """
                try:
                    self.w.statement_execution.execute_statement(
                        warehouse_id=self.warehouse_id,
                        statement=update_query,
                        wait_timeout="30s"
                    )
                except Exception as e:
                    print(f"Error marking step completed: {e}")
    
    def _add_action(self, state_id: str, action: Dict[str, Any]):
        """Add action to history"""
        state = self._get_journey_state(state_id)
        if state:
            actions_taken_str = state.get('actions_taken', '[]')
            if isinstance(actions_taken_str, str):
                try:
                    actions = json.loads(actions_taken_str)
                except:
                    actions = []
            else:
                actions = []
            actions.append(action)
            actions_json = json.dumps(actions).replace("'", "''")
            update_query = f"""
                UPDATE cdp_platform.core.customer_journey_states
                SET actions_taken = '{actions_json}',
                    last_action_at = current_timestamp()
                WHERE tenant_id = '{self.tenant_id}' AND state_id = '{state_id}'
            """
            try:
                self.w.statement_execution.execute_statement(
                    warehouse_id=self.warehouse_id,
                    statement=update_query,
                    wait_timeout="30s"
                )
            except Exception as e:
                print(f"Error adding action: {e}")
    
    def _exit_journey(self, state_id: str, exit_reason: str):
        """Exit a customer from journey"""
        exit_reason_escaped = exit_reason.replace("'", "''")
        update_query = f"""
            UPDATE cdp_platform.core.customer_journey_states
            SET status = 'exited',
                exit_reason = '{exit_reason_escaped}',
                completed_at = current_timestamp(),
                last_action_at = current_timestamp()
            WHERE tenant_id = '{self.tenant_id}' AND state_id = '{state_id}'
        """
        
        try:
            self.w.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=update_query,
                wait_timeout="30s"
            )
        except Exception as e:
            print(f"Error exiting journey: {e}")
    
    def _get_journey_state(self, state_id: str) -> Optional[Dict]:
        """Get journey state"""
        query = f"""
            SELECT *
            FROM cdp_platform.core.customer_journey_states
            WHERE tenant_id = '{self.tenant_id}' AND state_id = '{state_id}'
        """
        
        try:
            response = self.w.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=query,
                wait_timeout="30s"
            )
            
            if response.result and response.result.data_array:
                columns = [col.name for col in response.manifest.schema.columns] if response.manifest and response.manifest.schema else []
                row = response.result.data_array[0]
                row_dict = {columns[i]: row[i] for i in range(len(columns))}
                
                # Handle array conversion
                if 'steps_completed' in row_dict and isinstance(row_dict['steps_completed'], str):
                    try:
                        row_dict['steps_completed'] = json.loads(row_dict['steps_completed'])
                    except:
                        row_dict['steps_completed'] = []
                
                return row_dict
        except Exception as e:
            print(f"Error getting journey state: {e}")
        
        return None
    
    def get_journey_progress(self, journey_id: str) -> Dict[str, Any]:
        """Get journey progress analytics"""
        query = f"""
            SELECT 
                status,
                COUNT(*) as count
            FROM cdp_platform.core.customer_journey_states
            WHERE tenant_id = '{self.tenant_id}' AND journey_id = '{journey_id}'
            GROUP BY status
        """
        
        stats = {
            'active': 0,
            'waiting': 0,
            'completed': 0,
            'exited': 0,
            'error': 0
        }
        
        try:
            response = self.w.statement_execution.execute_statement(
                warehouse_id=self.warehouse_id,
                statement=query,
                wait_timeout="30s"
            )
            
            if response.result and response.result.data_array:
                columns = [col.name for col in response.manifest.schema.columns] if response.manifest and response.manifest.schema else []
                for row in response.result.data_array:
                    row_dict = {columns[i]: row[i] for i in range(len(columns))}
                    status = row_dict.get('status')
                    count = int(row_dict.get('count', 0) or 0)
                    if status in stats:
                        stats[status] = count
        except Exception as e:
            print(f"Error getting journey progress: {e}")
        
        return stats

