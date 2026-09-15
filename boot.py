"""
AI-OS Boot Harness.
Simulates Hardware Power-On Self-Test (POST) and initializes microkernel subsystems and Agent Orchestrator.
"""

import sys
import time
from ai_os.kernel.core import KernelCore
from ai_os.kernel.types import Capability, CapabilityType, SyscallCode, SyscallRequest
from ai_os.kernel.agent_api import AgentAPI
from ai_os.agents.orchestrator import AgentOrchestrator
from ai_os.agents.task_manifest import get_all_tasks


def run_post_diagnostics(kernel: KernelCore) -> bool:
    """Run Power-On Self-Test (POST) diagnostic checks."""
    print("[POST] Testing Security & Access Control...")
    pid = 999
    kernel.security.register_process(pid, capabilities=[Capability(CapabilityType.VFS_READ, "/etc/*")])
    if not kernel.security.check_capability(pid, CapabilityType.VFS_READ, "/etc/config"):
        print("[POST ERROR] Security Capability check failed!")
        return False
    if kernel.security.check_capability(pid, CapabilityType.VFS_WRITE, "/etc/config"):
        print("[POST ERROR] Security Capability violation allowed!")
        return False
    kernel.security.unregister_process(pid)

    print("[POST] Testing Memory Allocation & Isolation...")
    space = kernel.memory.create_space(pid)
    if not space.allocate(0x1000, 64) or not space.write(0x1000, b"POST_TEST"):
        print("[POST ERROR] Memory allocation/write failed!")
        return False
    if space.read(0x1000, 9) != b"POST_TEST":
        print("[POST ERROR] Memory read verification failed!")
        return False
    kernel.memory.destroy_space(pid)

    print("[POST] Testing VFS Operations...")
    kernel.security.register_process(pid, capabilities=[
        Capability(CapabilityType.VFS_WRITE, "/sys/*"),
        Capability(CapabilityType.VFS_READ, "/sys/*")
    ])
    if not kernel.vfs.write_file(pid, "/sys/boot.log", b"POST OK"):
        print("[POST ERROR] VFS Write failed!")
        return False
    if kernel.vfs.read_file(pid, "/sys/boot.log") != b"POST OK":
        print("[POST ERROR] VFS Read failed!")
        return False
    kernel.security.unregister_process(pid)

    print("[POST] All Diagnostic Checks Passed [OK]")
    return True


def main() -> int:
    print("=" * 60)
    print("        AI-OS MICROKERNEL BOOT HARNESS v0.1.0")
    print("=" * 60)

    kernel = KernelCore()

    start_time = time.perf_counter()
    if not run_post_diagnostics(kernel):
        print("\n[FATAL] Power-On Self-Test (POST) Failed. Aborting Boot.")
        return 1

    print("\n[BOOT] Booting Kernel Core...")
    kernel.boot()

    agent_api = AgentAPI(kernel)
    status = agent_api.get_system_status()
    elapsed = (time.perf_counter() - start_time) * 1000

    print(f"[BOOT] Kernel booted successfully in {elapsed:.2f}ms")
    print(f"[BOOT] Status: {status}")

    print("\n[BOOT] Booting Agent Orchestrator (Ecosystem Gateway)...")
    orchestrator = AgentOrchestrator(kernel)

    print("[POST] Onboarding Agent: Jules-Mutation-01...")
    jules_agent = orchestrator.onboard_agent(
        agent_id="jules-mut-01",
        name="Jules-Mutation-01",
        capabilities=[
            Capability(CapabilityType.AGENT_MUTATION, "*"),
            Capability(CapabilityType.AGENT_OBSERVATION, "*"),
            Capability(CapabilityType.VFS_READ, "/var/log/*"),
        ],
        lineage_id="lineage-jules-002",
    )
    print(f"[POST] Agent Onboarded Successfully (PID {jules_agent.pid}, ID {jules_agent.agent_id})")

    print("[POST] Loading 50 atomic tasks into mutation surface...")
    tasks = get_all_tasks()
    for task in tasks:
        orchestrator.submit_task(task)

    print(f"[BOOT COMPLETE] System ready. {len(tasks)} tasks pending in orchestrator pool.")

    # Spawn initial init process
    init_proc = kernel.create_process(
        name="init",
        priority=1,
        capabilities=[Capability(CapabilityType.ADMIN, "*")],
    )
    print(f"[BOOT] Created Init Process (PID {init_proc.pid})")

    # Perform sample syscall via agent API
    sys_res = agent_api.execute_syscall(
        pid=init_proc.pid,
        code="SYS_VFS_WRITE",
        args={"path": "/var/log/system.log", "content": b"AI-OS Initialized Successfully."},
    )
    print(f"[BOOT] System Init Syscall Result: {sys_res}")

    print("\n[AI-OS] System operational and ready for agent commands.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
