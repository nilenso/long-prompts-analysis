# SWE-bench Pro Task Runner

.PHONY: help run run-all-agents run-all cleanup list-tasks list-agents status

# Available tasks and agents
TASKS := subdomain qt_warning changelog parse_duration later_units coord_parsing process_cleanup close_matches search_flags untrusted_args
AGENTS := opus-codex opus-claude gpt-codex gpt-claude opus-empty gpt-empty

# Task script paths
TASK_subdomain := scripts/tasks/task_c580ebf0_subdomain_blocking.sh
TASK_qt_warning := scripts/tasks/task_f91ace96_qt_warning.sh
TASK_changelog := scripts/tasks/task_f631cd44_changelog.sh
TASK_parse_duration := scripts/tasks/task_96b99780_parse_duration.sh
TASK_later_units := scripts/tasks/task_70248f25_later_units.sh
TASK_coord_parsing := scripts/tasks/task_85b867fe_coord_parsing.sh
TASK_process_cleanup := scripts/tasks/task_c09e1439_process_cleanup.sh
TASK_close_matches := scripts/tasks/task_a84ecfb8_close_matches.sh
TASK_search_flags := scripts/tasks/task_bf045f7e_search_flags.sh
TASK_untrusted_args := scripts/tasks/task_8f46ba3f_untrusted_args.sh

help:
	@echo "SWE-bench Pro Task Runner"
	@echo "========================="
	@echo ""
	@echo "Single run:"
	@echo "  make run TASK=<task> AGENT=<agent>"
	@echo ""
	@echo "Parallel runs:"
	@echo "  make run-all-agents TASK=<task>    # Run all 6 agents on one task"
	@echo "  make run-all                       # Run all 10 tasks × 6 agents (60 runs)"
	@echo ""
	@echo "Utilities:"
	@echo "  make cleanup                       # Remove all worktrees"
	@echo "  make list-tasks                    # List available tasks"
	@echo "  make list-agents                   # List available agents"
	@echo "  make status                        # Show worktree status"
	@echo ""
	@echo "Tasks: $(TASKS)"
	@echo "Agents: $(AGENTS)"
	@echo ""
	@echo "Examples:"
	@echo "  make run TASK=subdomain AGENT=opus-claude"
	@echo "  make run-all-agents TASK=parse_duration"
	@echo "  make run-all"

# Single task + single agent
run:
ifndef TASK
	@echo "Error: TASK required. Use: make run TASK=<task> AGENT=<agent>"
	@exit 1
endif
ifndef AGENT
	@echo "Error: AGENT required. Use: make run TASK=<task> AGENT=<agent>"
	@exit 1
endif
	@TASK_SCRIPT="$(TASK_$(TASK))"; \
	if [ -z "$$TASK_SCRIPT" ]; then \
		echo "Error: Unknown task '$(TASK)'"; \
		echo "Available: $(TASKS)"; \
		exit 1; \
	fi; \
	./scripts/run_task.sh "$$TASK_SCRIPT" "$(AGENT)"

# Single task + all agents (6 parallel)
run-all-agents:
ifndef TASK
	@echo "Error: TASK required. Use: make run-all-agents TASK=<task>"
	@exit 1
endif
	@TASK_SCRIPT="$(TASK_$(TASK))"; \
	if [ -z "$$TASK_SCRIPT" ]; then \
		echo "Error: Unknown task '$(TASK)'"; \
		exit 1; \
	fi; \
	echo "Running $(TASK) with all agents in parallel..."; \
	for agent in $(AGENTS); do \
		./scripts/run_task.sh "$$TASK_SCRIPT" "$$agent" & \
	done; \
	wait; \
	echo "All agents completed for $(TASK)"

# All tasks × all agents (60 parallel)
run-all:
	@echo "Running all tasks × all agents (60 parallel runs)..."
	@for agent in $(AGENTS); do \
		./scripts/run_task.sh $(TASK_subdomain) $$agent & \
		./scripts/run_task.sh $(TASK_qt_warning) $$agent & \
		./scripts/run_task.sh $(TASK_changelog) $$agent & \
		./scripts/run_task.sh $(TASK_parse_duration) $$agent & \
		./scripts/run_task.sh $(TASK_later_units) $$agent & \
		./scripts/run_task.sh $(TASK_coord_parsing) $$agent & \
		./scripts/run_task.sh $(TASK_process_cleanup) $$agent & \
		./scripts/run_task.sh $(TASK_close_matches) $$agent & \
		./scripts/run_task.sh $(TASK_search_flags) $$agent & \
		./scripts/run_task.sh $(TASK_untrusted_args) $$agent & \
	done; \
	wait; \
	echo "All 60 runs completed"

cleanup:
	@./scripts/cleanup_worktrees.sh --force

list-tasks:
	@echo "Available tasks:"
	@echo "  subdomain        - Host blocking subdomains"
	@echo "  qt_warning       - Qt warning filtering"
	@echo "  changelog        - Changelog upgrade filtering"
	@echo "  parse_duration   - Duration parsing validation"
	@echo "  later_units      - Add units to :later command"
	@echo "  coord_parsing    - Coordinate string parsing"
	@echo "  process_cleanup  - Process data cleanup"
	@echo "  close_matches    - Close matches for invalid commands"
	@echo "  search_flags     - Search direction flags fix"
	@echo "  untrusted_args   - Untrusted CLI arguments handling"

list-agents:
	@echo "Available agents:"
	@echo "  opus-codex   - Claude Opus 4.5 + Codex prompt"
	@echo "  opus-claude  - Claude Opus 4.5 + Claude Code prompt"
	@echo "  gpt-codex    - GPT 5.2 + Codex prompt"
	@echo "  gpt-claude   - GPT 5.2 + Claude Code prompt"
	@echo "  opus-empty   - Claude Opus 4.5 + no system prompt"
	@echo "  gpt-empty    - GPT 5.2 + no system prompt"

status:
	@echo "Worktrees:"
	@git -C qutebrowser worktree list
	@echo ""
	@echo "Worktree dirs:"
	@ls -d worktrees/*/ 2>/dev/null || echo "  (none)"
