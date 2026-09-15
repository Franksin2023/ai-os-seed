"""
Atomic Task Manifest for AI-OS Ecosystem
50 mutation tasks organized by subsystem priority.
"""

import os
import subprocess
from typing import Callable, List
from ai_os.agents.orchestrator import AgentTask
from ai_os.kernel.types import CapabilityType


def _check_file_exists(filepath: str) -> bool:
    """Check if a file exists in the repository."""
    return os.path.exists(filepath)


def _check_function_exists(filepath: str, function_name: str) -> bool:
    """Check if a function exists in a Python file."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            return f"def {function_name}" in content
    except Exception:
        return False


def _check_class_exists(filepath: str, class_name: str) -> bool:
    """Check if a class exists in a Python file."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            return f"class {class_name}" in content
    except Exception:
        return False


def _run_test(test_name: str) -> bool:
    """Run a specific pytest test and return True if it passes."""
    try:
        result = subprocess.run(
            ["python3", "-m", "pytest", f"tests/{test_name}.py", "-v"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0
    except Exception:
        return False


# ============================================================================
# IPC ENHANCEMENTS (Tasks 1-10)
# ============================================================================

TASK_001 = AgentTask(
    task_id="IPC-001",
    description="Add shared memory IPC primitive allowing processes to map the same memory region",
    required_capabilities=[CapabilityType.IPC_SEND, CapabilityType.MEMORY_ALLOC],
    fitness_function=lambda: _check_file_exists("ai_os/kernel/ipc.py") and _check_function_exists("ai_os/kernel/ipc.py", "create_shared_memory"),
    adr_required=True
)

TASK_002 = AgentTask(
    task_id="IPC-002",
    description="Implement pub-sub channel with topic-based message routing",
    required_capabilities=[CapabilityType.IPC_SEND],
    fitness_function=lambda: _check_class_exists("ai_os/kernel/ipc.py", "PubSubChannel") and _run_test("test_pubsub_basic"),
    adr_required=True
)

TASK_003 = AgentTask(
    task_id="IPC-003",
    description="Add IPC queue overflow protection with configurable size limits",
    required_capabilities=[CapabilityType.IPC_SEND],
    fitness_function=lambda: _run_test("test_ipc_queue_overflow_protection"),
    adr_required=True
)

TASK_004 = AgentTask(
    task_id="IPC-004",
    description="Implement capability-gated IPC endpoint discovery",
    required_capabilities=[CapabilityType.IPC_SEND, CapabilityType.SYSCALL_EXEC],
    fitness_function=lambda: _run_test("test_ipc_endpoint_discovery"),
    adr_required=True
)

TASK_005 = AgentTask(
    task_id="IPC-005",
    description="Add IPC message priority queue with deadline-based scheduling",
    required_capabilities=[CapabilityType.IPC_SEND],
    fitness_function=lambda: _run_test("test_ipc_priority_queue"),
    adr_required=True
)

TASK_006 = AgentTask(
    task_id="IPC-006",
    description="Implement IPC channel telemetry with message count and latency metrics",
    required_capabilities=[CapabilityType.IPC_SEND],
    fitness_function=lambda: _run_test("test_ipc_telemetry_metrics"),
    adr_required=True
)

TASK_007 = AgentTask(
    task_id="IPC-007",
    description="Add IPC message serialization/deserialization with type safety",
    required_capabilities=[CapabilityType.IPC_SEND],
    fitness_function=lambda: _run_test("test_ipc_message_serialization"),
    adr_required=True
)

TASK_008 = AgentTask(
    task_id="IPC-008",
    description="Implement IPC channel cleanup on process termination",
    required_capabilities=[CapabilityType.IPC_SEND, CapabilityType.PROCESS_KILL],
    fitness_function=lambda: _run_test("test_ipc_cleanup_on_terminate"),
    adr_required=True
)

TASK_009 = AgentTask(
    task_id="IPC-009",
    description="Add IPC broadcast mechanism for system-wide notifications",
    required_capabilities=[CapabilityType.IPC_SEND, CapabilityType.ADMIN],
    fitness_function=lambda: _run_test("test_ipc_broadcast"),
    adr_required=True
)

TASK_010 = AgentTask(
    task_id="IPC-010",
    description="Implement IPC channel health check and auto-recovery",
    required_capabilities=[CapabilityType.IPC_SEND],
    fitness_function=lambda: _run_test("test_ipc_health_check"),
    adr_required=True
)

# ============================================================================
# MEMORY MANAGEMENT (Tasks 11-20)
# ============================================================================

TASK_011 = AgentTask(
    task_id="MEM-011",
    description="Implement LRU eviction policy for memory pages",
    required_capabilities=[CapabilityType.MEMORY_ALLOC, CapabilityType.MEMORY_WRITE],
    fitness_function=lambda: _run_test("test_memory_lru_eviction"),
    adr_required=True
)

TASK_012 = AgentTask(
    task_id="MEM-012",
    description="Add memory fragmentation detection and compaction",
    required_capabilities=[CapabilityType.MEMORY_ALLOC],
    fitness_function=lambda: _run_test("test_memory_fragmentation_detection"),
    adr_required=True
)

TASK_013 = AgentTask(
    task_id="MEM-013",
    description="Implement memory usage telemetry with per-process breakdown",
    required_capabilities=[CapabilityType.MEMORY_READ],
    fitness_function=lambda: _run_test("test_memory_telemetry_per_process"),
    adr_required=True
)

TASK_014 = AgentTask(
    task_id="MEM-014",
    description="Add memory quota enforcement with OOM killer integration",
    required_capabilities=[CapabilityType.MEMORY_ALLOC, CapabilityType.PROCESS_KILL],
    fitness_function=lambda: _run_test("test_memory_quota_enforcement"),
    adr_required=True
)

TASK_015 = AgentTask(
    task_id="MEM-015",
    description="Implement memory page protection flags (read-only, execute-only)",
    required_capabilities=[CapabilityType.MEMORY_WRITE, CapabilityType.ADMIN],
    fitness_function=lambda: _run_test("test_memory_page_protection"),
    adr_required=True
)

TASK_016 = AgentTask(
    task_id="MEM-016",
    description="Add memory allocation failure simulation for testing",
    required_capabilities=[CapabilityType.MEMORY_ALLOC, CapabilityType.ADMIN],
    fitness_function=lambda: _run_test("test_memory_allocation_failure"),
    adr_required=True
)

TASK_017 = AgentTask(
    task_id="MEM-017",
    description="Implement memory pool allocator for fixed-size objects",
    required_capabilities=[CapabilityType.MEMORY_ALLOC],
    fitness_function=lambda: _run_test("test_memory_pool_allocator"),
    adr_required=True
)

TASK_018 = AgentTask(
    task_id="MEM-018",
    description="Add memory leak detection via reference counting",
    required_capabilities=[CapabilityType.MEMORY_READ],
    fitness_function=lambda: _run_test("test_memory_leak_detection"),
    adr_required=True
)

TASK_019 = AgentTask(
    task_id="MEM-019",
    description="Implement memory defragmentation during idle CPU ticks",
    required_capabilities=[CapabilityType.MEMORY_WRITE],
    fitness_function=lambda: _run_test("test_memory_defrag_idle"),
    adr_required=True
)

TASK_020 = AgentTask(
    task_id="MEM-020",
    description="Add memory allocation statistics and historical tracking",
    required_capabilities=[CapabilityType.MEMORY_READ],
    fitness_function=lambda: _run_test("test_memory_allocation_stats"),
    adr_required=True
)

# ============================================================================
# VFS PERSISTENCE (Tasks 21-30)
# ============================================================================

TASK_021 = AgentTask(
    task_id="VFS-021",
    description="Implement VFS persistence layer with JSON-based state serialization",
    required_capabilities=[CapabilityType.VFS_WRITE],
    fitness_function=lambda: _run_test("test_vfs_persistence_json"),
    adr_required=True
)

TASK_022 = AgentTask(
    task_id="VFS-022",
    description="Add VFS transaction support with rollback capability",
    required_capabilities=[CapabilityType.VFS_WRITE],
    fitness_function=lambda: _run_test("test_vfs_transaction_rollback"),
    adr_required=True
)

TASK_023 = AgentTask(
    task_id="VFS-023",
    description="Implement VFS file locking with deadlock detection",
    required_capabilities=[CapabilityType.VFS_WRITE],
    fitness_function=lambda: _run_test("test_vfs_file_locking"),
    adr_required=True
)

TASK_024 = AgentTask(
    task_id="VFS-024",
    description="Add VFS directory tree traversal with depth limits",
    required_capabilities=[CapabilityType.VFS_READ],
    fitness_function=lambda: _run_test("test_vfs_directory_traversal"),
    adr_required=True
)

TASK_025 = AgentTask(
    task_id="VFS-025",
    description="Implement VFS file metadata (creation time, modification time, size)",
    required_capabilities=[CapabilityType.VFS_WRITE],
    fitness_function=lambda: _run_test("test_vfs_file_metadata"),
    adr_required=True
)

TASK_026 = AgentTask(
    task_id="VFS-026",
    description="Add VFS capability-based path access control",
    required_capabilities=[CapabilityType.VFS_WRITE],
    fitness_function=lambda: _run_test("test_vfs_path_access_control"),
    adr_required=True
)

TASK_027 = AgentTask(
    task_id="VFS-027",
    description="Implement VFS file compression for large objects",
    required_capabilities=[CapabilityType.VFS_WRITE],
    fitness_function=lambda: _run_test("test_vfs_file_compression"),
    adr_required=True
)

TASK_028 = AgentTask(
    task_id="VFS-028",
    description="Add VFS snapshot and restore functionality",
    required_capabilities=[CapabilityType.VFS_WRITE, CapabilityType.ADMIN],
    fitness_function=lambda: _run_test("test_vfs_snapshot_restore"),
    adr_required=True
)

TASK_029 = AgentTask(
    task_id="VFS-029",
    description="Implement VFS garbage collection for orphaned files",
    required_capabilities=[CapabilityType.VFS_WRITE],
    fitness_function=lambda: _run_test("test_vfs_garbage_collection"),
    adr_required=True
)

TASK_030 = AgentTask(
    task_id="VFS-030",
    description="Add VFS read/write performance metrics and bottleneck detection",
    required_capabilities=[CapabilityType.VFS_READ],
    fitness_function=lambda: _run_test("test_vfs_performance_metrics"),
    adr_required=True
)

# ============================================================================
# PROCESS MANAGEMENT (Tasks 31-40)
# ============================================================================

TASK_031 = AgentTask(
    task_id="PROC-031",
    description="Implement process group management with group-based signaling",
    required_capabilities=[CapabilityType.PROCESS_SPAWN, CapabilityType.PROCESS_KILL],
    fitness_function=lambda: _run_test("test_process_group_management"),
    adr_required=True
)

TASK_032 = AgentTask(
    task_id="PROC-032",
    description="Add orphaned process detection and automatic cleanup",
    required_capabilities=[CapabilityType.PROCESS_KILL],
    fitness_function=lambda: _run_test("test_orphaned_process_cleanup"),
    adr_required=True
)

TASK_033 = AgentTask(
    task_id="PROC-033",
    description="Implement process priority inheritance for resource contention",
    required_capabilities=[CapabilityType.PROCESS_SPAWN],
    fitness_function=lambda: _run_test("test_process_priority_inheritance"),
    adr_required=True
)

TASK_034 = AgentTask(
    task_id="PROC-034",
    description="Add process CPU usage tracking and throttling",
    required_capabilities=[CapabilityType.PROCESS_SPAWN],
    fitness_function=lambda: _run_test("test_process_cpu_throttling"),
    adr_required=True
)

TASK_035 = AgentTask(
    task_id="PROC-035",
    description="Implement process checkpoint and restore for migration",
    required_capabilities=[CapabilityType.PROCESS_SPAWN, CapabilityType.MEMORY_READ],
    fitness_function=lambda: _run_test("test_process_checkpoint_restore"),
    adr_required=True
)

TASK_036 = AgentTask(
    task_id="PROC-036",
    description="Add process resource usage quotas (CPU, memory, IPC)",
    required_capabilities=[CapabilityType.PROCESS_SPAWN],
    fitness_function=lambda: _run_test("test_process_resource_quotas"),
    adr_required=True
)

TASK_037 = AgentTask(
    task_id="PROC-037",
    description="Implement process signal handler registration and dispatch",
    required_capabilities=[CapabilityType.PROCESS_SPAWN],
    fitness_function=lambda: _run_test("test_process_signal_handler"),
    adr_required=True
)

TASK_038 = AgentTask(
    task_id="PROC-038",
    description="Add process lifecycle state machine (created, running, sleeping, zombie)",
    required_capabilities=[CapabilityType.PROCESS_SPAWN],
    fitness_function=lambda: _run_test("test_process_state_machine"),
    adr_required=True
)

TASK_039 = AgentTask(
    task_id="PROC-039",
    description="Implement process tree visualization and debugging interface",
    required_capabilities=[CapabilityType.PROCESS_SPAWN],
    fitness_function=lambda: _run_test("test_process_tree_visualization"),
    adr_required=True
)

TASK_040 = AgentTask(
    task_id="PROC-040",
    description="Add process exit code tracking and parent notification",
    required_capabilities=[CapabilityType.PROCESS_KILL, CapabilityType.IPC_SEND],
    fitness_function=lambda: _run_test("test_process_exit_notification"),
    adr_required=True
)

# ============================================================================
# AGENT RPC & DIAGNOSTICS (Tasks 41-50)
# ============================================================================

TASK_041 = AgentTask(
    task_id="AGENT-041",
    description="Implement agent RPC method discovery and introspection",
    required_capabilities=[CapabilityType.AGENT_OBSERVATION],
    fitness_function=lambda: _run_test("test_agent_rpc_discovery"),
    adr_required=True
)

TASK_042 = AgentTask(
    task_id="AGENT-042",
    description="Add agent health check endpoint with detailed diagnostics",
    required_capabilities=[CapabilityType.AGENT_OBSERVATION],
    fitness_function=lambda: _run_test("test_agent_health_check"),
    adr_required=True
)

TASK_043 = AgentTask(
    task_id="AGENT-043",
    description="Implement agent auto-repair for detected anomalies",
    required_capabilities=[CapabilityType.AGENT_MUTATION],
    fitness_function=lambda: _run_test("test_agent_auto_repair"),
    adr_required=True
)

TASK_044 = AgentTask(
    task_id="AGENT-044",
    description="Add agent performance scoring and leaderboard tracking",
    required_capabilities=[CapabilityType.AGENT_OBSERVATION],
    fitness_function=lambda: _run_test("test_agent_performance_scoring"),
    adr_required=True
)

TASK_045 = AgentTask(
    task_id="AGENT-045",
    description="Implement agent task retry logic with exponential backoff",
    required_capabilities=[CapabilityType.AGENT_MUTATION],
    fitness_function=lambda: _run_test("test_agent_task_retry"),
    adr_required=True
)

TASK_046 = AgentTask(
    task_id="AGENT-046",
    description="Add agent capability verification before task assignment",
    required_capabilities=[CapabilityType.AGENT_OBSERVATION],
    fitness_function=lambda: _run_test("test_agent_capability_verification"),
    adr_required=True
)

TASK_047 = AgentTask(
    task_id="AGENT-047",
    description="Implement agent lineage tracking across multiple generations",
    required_capabilities=[CapabilityType.AGENT_OBSERVATION],
    fitness_function=lambda: _run_test("test_agent_lineage_tracking"),
    adr_required=True
)

TASK_048 = AgentTask(
    task_id="AGENT-048",
    description="Add agent resource usage monitoring and automatic scaling",
    required_capabilities=[CapabilityType.AGENT_OBSERVATION],
    fitness_function=lambda: _run_test("test_agent_resource_monitoring"),
    adr_required=True
)

TASK_049 = AgentTask(
    task_id="AGENT-049",
    description="Implement agent sandbox escape detection and prevention",
    required_capabilities=[CapabilityType.AGENT_OBSERVATION],
    fitness_function=lambda: _run_test("test_agent_sandbox_escape_detection"),
    adr_required=True
)

TASK_050 = AgentTask(
    task_id="AGENT-050",
    description="Add agent collaborative task execution with result aggregation",
    required_capabilities=[CapabilityType.AGENT_MUTATION, CapabilityType.IPC_SEND],
    fitness_function=lambda: _run_test("test_agent_collaborative_execution"),
    adr_required=True
)


def get_all_tasks() -> List[AgentTask]:
    """Return all 50 atomic tasks for the orchestrator."""
    return [
        TASK_001, TASK_002, TASK_003, TASK_004, TASK_005,
        TASK_006, TASK_007, TASK_008, TASK_009, TASK_010,
        TASK_011, TASK_012, TASK_013, TASK_014, TASK_015,
        TASK_016, TASK_017, TASK_018, TASK_019, TASK_020,
        TASK_021, TASK_022, TASK_023, TASK_024, TASK_025,
        TASK_026, TASK_027, TASK_028, TASK_029, TASK_030,
        TASK_031, TASK_032, TASK_033, TASK_034, TASK_035,
        TASK_036, TASK_037, TASK_038, TASK_039, TASK_040,
        TASK_041, TASK_042, TASK_043, TASK_044, TASK_045,
        TASK_046, TASK_047, TASK_048, TASK_049, TASK_050
    ]


def get_tasks_by_category(category: str) -> List[AgentTask]:
    """Return tasks filtered by category (IPC, MEM, VFS, PROC, AGENT)."""
    all_tasks = get_all_tasks()
    return [task for task in all_tasks if task.task_id.startswith(category)]
