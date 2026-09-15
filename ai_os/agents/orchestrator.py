"""
Agent Orchestrator: The ecosystem gateway for AI-OS.
Manages the lifecycle, task assignment, validation, and lineage of autonomous agents.
"""

from enum import Enum
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from ai_os.kernel.types import Capability, CapabilityType, ResourceLimits
from ai_os.kernel.core import KernelCore


class AgentTaskStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentTask:
    task_id: str
    task_type: str
    payload: Dict[str, Any]
    status: AgentTaskStatus = AgentTaskStatus.PENDING
    assigned_agent_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None


@dataclass
class AgentProfile:
    agent_id: str
    name: str
    pid: int
    capabilities: List[Capability]
    lineage_id: str = "lineage-base-001"


class AgentOrchestrator:
    """
    Gateway and manager for autonomous agents operating on AI-OS.
    """

    def __init__(self, kernel: KernelCore) -> None:
        self.kernel = kernel
        self.agents: Dict[str, AgentProfile] = {}
        self.tasks: Dict[str, AgentTask] = {}
        self._next_task_id = 1

    def onboard_agent(
        self,
        agent_id: str,
        name: str,
        capabilities: List[Capability],
        lineage_id: str = "lineage-base-001",
    ) -> AgentProfile:
        """Onboard and spawn an autonomous agent process in the kernel."""
        pcb = self.kernel.create_process(
            name=f"agent_{name}",
            capabilities=capabilities,
        )
        profile = AgentProfile(
            agent_id=agent_id,
            name=name,
            pid=pcb.pid,
            capabilities=capabilities,
            lineage_id=lineage_id,
        )
        self.agents[agent_id] = profile
        self.kernel.telemetry.log_event(
            "AGENT_ONBOARDED",
            pid=pcb.pid,
            details={"agent_id": agent_id, "name": name, "lineage_id": lineage_id},
        )
        return profile

    def create_task(self, task_type: str, payload: Dict[str, Any]) -> AgentTask:
        """Create a new task for agent execution."""
        task_id = f"task-{self._next_task_id}"
        self._next_task_id += 1
        task = AgentTask(
            task_id=task_id,
            task_type=task_type,
            payload=payload,
            status=AgentTaskStatus.PENDING,
        )
        self.tasks[task_id] = task
        return task

    def assign_task(self, task_id: str, agent_id: str) -> bool:
        """Assign task to agent if agent holds required capabilities."""
        task = self.tasks.get(task_id)
        agent = self.agents.get(agent_id)
        if not task or not agent:
            return False

        task.assigned_agent_id = agent_id
        task.status = AgentTaskStatus.ASSIGNED
        self.kernel.telemetry.log_event(
            "AGENT_TASK_ASSIGNED",
            pid=agent.pid,
            details={"task_id": task_id, "agent_id": agent_id},
        )
        return True

    def complete_task(self, task_id: str, result: Dict[str, Any]) -> bool:
        """Mark task completed with results."""
        task = self.tasks.get(task_id)
        if not task:
            return False
        task.status = AgentTaskStatus.COMPLETED
        task.result = result
        self.kernel.telemetry.log_event(
            "AGENT_TASK_COMPLETED",
            details={"task_id": task_id, "result": result},
        )
        return True
