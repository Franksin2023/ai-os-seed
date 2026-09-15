"""
Unit and integration test suite for AI-OS kernel and emergent subsystems.
"""

import pytest
from ai_os.kernel.core import KernelCore
from ai_os.kernel.types import (
    Capability,
    CapabilityType,
    ProcessState,
    ResourceLimits,
    SyscallCode,
    SyscallRequest,
)
from ai_os.kernel.agent_api import AgentAPI
from evolution_internal import run_internal_evolution_cycle
from evolution_emergent import run_emergent_evolution_cycle
from behaviour_orchestrator import run_episode
from task_executor import execute_task
from ai_os.emergent_scheduler import EmergentScheduler, SchedulerTraits
from ai_os.emergent_memory import EmergentMemoryModel, MemoryTraits
from ai_os.emergent_vfs import EmergentVFS, VFSTraits
from ai_os.emergent_hal import EmergentHAL, HALTraits
from ai_os.emergent_runtime import EmergentRuntime, RuntimeTraits
from ai_os.agents.orchestrator import AgentOrchestrator, AgentTaskStatus
from ai_os.agents.task_manifest import get_all_tasks, get_tasks_by_category


@pytest.fixture
def kernel():
    k = KernelCore()
    k.boot()
    return k


def test_kernel_boot(kernel):
    assert kernel.is_booted is True
    events = kernel.telemetry.get_events()
    assert len(events) >= 2
    assert events[0].event_type == "BOOT_START"
    assert events[1].event_type == "BOOT_COMPLETE"


def test_process_lifecycle(kernel):
    pcb = kernel.create_process(name="worker", priority=5)
    assert pcb.pid == 1
    assert pcb.name == "worker"
    assert pcb.state == ProcessState.READY

    scheduled = kernel.scheduler.schedule()
    assert scheduled.pid == 1
    assert scheduled.state == ProcessState.RUNNING

    terminated = kernel.terminate_process(1)
    assert terminated is True
    assert kernel.scheduler.get_process(1).state == ProcessState.TERMINATED


def test_security_capabilities(kernel):
    caps = [Capability(CapabilityType.VFS_READ, "/app/*")]
    pcb = kernel.create_process(name="sandboxed", capabilities=caps)

    # Allowed path
    assert kernel.security.check_capability(pcb.pid, CapabilityType.VFS_READ, "/app/config.json") is True
    # Denied path
    assert kernel.security.check_capability(pcb.pid, CapabilityType.VFS_READ, "/etc/shadow") is False
    # Denied permission
    assert kernel.security.check_capability(pcb.pid, CapabilityType.VFS_WRITE, "/app/config.json") is False


def test_memory_isolation(kernel):
    p1 = kernel.create_process(name="p1")
    p2 = kernel.create_process(name="p2")

    space1 = kernel.memory.get_space(p1.pid)
    space2 = kernel.memory.get_space(p2.pid)

    assert space1.allocate(0x1000, 100) is True
    assert space2.allocate(0x1000, 100) is True

    space1.write(0x1000, b"P1_DATA")
    space2.write(0x1000, b"P2_DATA")

    assert space1.read(0x1000, 7) == b"P1_DATA"
    assert space2.read(0x1000, 7) == b"P2_DATA"


def test_vfs_capability_enforcement(kernel):
    caps = [
        Capability(CapabilityType.VFS_WRITE, "/tmp/*"),
        Capability(CapabilityType.VFS_READ, "/tmp/*"),
    ]
    p = kernel.create_process(name="writer", capabilities=caps)

    # Write allowed
    res_w = kernel.vfs.write_file(p.pid, "/tmp/hello.txt", b"Hello VFS")
    assert res_w is True

    # Read allowed
    res_r = kernel.vfs.read_file(p.pid, "/tmp/hello.txt")
    assert res_r == b"Hello VFS"

    # Write denied (outside /tmp/*)
    res_w_denied = kernel.vfs.write_file(p.pid, "/etc/config", b"hack")
    assert res_w_denied is False


def test_ipc(kernel):
    c1 = Capability(CapabilityType.IPC_SEND, "channel_1")
    c2 = Capability(CapabilityType.IPC_RECEIVE, "channel_1")

    p1 = kernel.create_process(name="sender", capabilities=[c1])
    p2 = kernel.create_process(name="receiver", capabilities=[c2])

    # Send message
    ok = kernel.ipc.send_message(p1.pid, p2.pid, "channel_1", {"msg": "ping"})
    assert ok is True

    # Receive message
    msg = kernel.ipc.receive_message(p2.pid, "channel_1")
    assert msg is not None
    assert msg.sender_pid == p1.pid
    assert msg.payload == {"msg": "ping"}


def test_syscall_dispatcher(kernel):
    caps = [Capability(CapabilityType.VFS_WRITE, "/logs/*")]
    p = kernel.create_process(name="logger", capabilities=caps)

    req = SyscallRequest(
        pid=p.pid,
        code=SyscallCode.VFS_WRITE,
        args={"path": "/logs/test.log", "content": b"Log entry"},
    )
    resp = kernel.syscall(req)
    assert resp.success is True

    # Check telemetry audit
    telemetry_events = kernel.telemetry.get_events(event_type="SYSCALL_EXECUTE", pid=p.pid)
    assert len(telemetry_events) == 1
    assert telemetry_events[0].details["code"] == "SYS_VFS_WRITE"
    assert telemetry_events[0].details["success"] is True


def test_agent_api(kernel):
    agent_api = AgentAPI(kernel)

    status = agent_api.get_system_status()
    assert status["booted"] is True

    p = kernel.create_process(
        name="agent_proc",
        capabilities=[Capability(CapabilityType.ADMIN, "*")],
    )

    info = agent_api.inspect_process(p.pid)
    assert info["pid"] == p.pid
    assert info["name"] == "agent_proc"

    sys_res = agent_api.execute_syscall(
        pid=p.pid,
        code="SYS_VFS_WRITE",
        args={"path": "/admin/secret", "content": b"classified"},
    )
    assert sys_res["success"] is True


def test_internal_evolution_cycle():
    res = run_internal_evolution_cycle("moderate")
    assert res["status"] == "success"
    assert res["cycle_type"] == "moderate"
    assert res["pressure_log"]["mutations_executed"] == 5
    assert "champion" in res


def test_emergent_subsystems():
    sched = EmergentScheduler(SchedulerTraits(time_slice_ms=10, fairness_mode="cfs", priority_weights={"high": 1.5}))
    mem = EmergentMemoryModel(MemoryTraits(allocation_strategy="buddy", fragmentation_threshold=0.2, paging_mode="demand"))
    vfs = EmergentVFS(VFSTraits(persistence_mode="in_memory", indexing_strategy="btree", cache_policy="lru"))
    hal = EmergentHAL(HALTraits(init_sequence="fast", timeout_ms=500, driver_profile="minimal"))
    runtime = EmergentRuntime(RuntimeTraits(interaction_mode="rpc", process_model="microkernel", logging_verbosity="info"))

    sched.apply_traits()
    mem.apply_traits()
    vfs.apply_traits()
    hal.apply_traits()
    runtime.apply_traits()

    assert sched.fitness_hooks()["time_slice_ms"] == 10
    assert mem.fitness_hooks()["allocation_strategy"] == "buddy"
    assert vfs.fitness_hooks()["persistence_mode"] == "in_memory"
    assert hal.fitness_hooks()["driver_profile"] == "minimal"
    assert runtime.fitness_hooks()["interaction_mode"] == "rpc"

    # Test compute_fitness hooks
    assert sched.compute_fitness({"tsu": 0.9, "pds": 0.8, "si": 0}) > 0.5
    assert mem.compute_fitness({"efficiency": 0.9, "fragmentation": 0.1}) > 0.5
    assert vfs.compute_fitness({"lookup_speed_score": 0.9, "reliability_score": 0.9}) == 0.9
    assert hal.compute_fitness({"init_success_rate": 1.0, "timeout_stability": 0.9}) > 0.8
    assert runtime.compute_fitness({"responsiveness": 0.9, "process_handling": 0.9}) == 0.9


def test_emergent_evolution_cycle():
    res = run_emergent_evolution_cycle("moderate")
    assert res["status"] == "success"
    assert res["cycle_type"] == "moderate"
    assert "initial_traits" in res
    assert "subsystem_log" in res


def test_behaviour_orchestrator_episode():
    res = run_episode({"episode_id": "ep-test-01", "duration": 50}, "kernel-lineage-042")
    assert res["status"] == "completed"
    assert res["lineage_id"] == "kernel-lineage-042"
    assert "behaviour_fitness" in res
    assert res["behaviour_fitness"] > 0.5


def test_task_executor():
    task_cfg = {
        "name": "process_lifecycle",
        "steps": ["create", "allocate_memory", "vfs_write", "terminate"],
    }
    res = execute_task(task_cfg, "kernel-lineage-063")
    assert res["lineage_id"] == "kernel-lineage-063"
    assert res["task"] == "process_lifecycle"
    assert res["task_fitness"] > 0.5


def test_agent_orchestrator_manifest(kernel):
    orchestrator = AgentOrchestrator(kernel)
    agent = orchestrator.onboard_agent(
        agent_id="test-agent-01",
        name="TestAgent",
        capabilities=[Capability(CapabilityType.AGENT_MUTATION, "*")],
    )
    assert agent.agent_id == "test-agent-01"

    tasks = get_all_tasks()
    assert len(tasks) == 50

    ipc_tasks = get_tasks_by_category("IPC")
    assert len(ipc_tasks) == 10

    for t in tasks:
        orchestrator.submit_task(t)

    assert len(orchestrator.tasks) == 50
    assert orchestrator.tasks["IPC-001"].description != ""
