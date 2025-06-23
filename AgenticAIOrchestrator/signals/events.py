from blinker import Namespace

event_signals = Namespace()

agent_status_changed = event_signals.signal('agent_status_changed')
tool_status_changed = event_signals.signal('tool_status_changed')
task_status_changed = event_signals.signal('task_status_changed')
log_created = event_signals.signal('log_created') 