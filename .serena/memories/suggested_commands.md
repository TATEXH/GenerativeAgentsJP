# Suggested Commands for GenerativeAgentsJP

## Environment Setup
**CRITICAL**: Always activate conda environment before any Python operations:
```bash
conda activate generative_agents_jp
```

## Core Simulation Commands

### Start New Simulation
```bash
cd generative_agents
python start.py --name sim-test --start "20250213-09:30" --step 10 --stride 10
```

### Resume Simulation
```bash
cd generative_agents
python start.py --name sim-test --resume --step 10 --stride 10
```

### Generate Replay Data
```bash
cd generative_agents
python compress.py --name <simulation-name>
```

### Start Replay Server
```bash
cd generative_agents
python replay.py
```
Access via browser: `http://127.0.0.1:5000/?name=<simulation-name>`

## Development Commands

### Project Scripts
```bash
# Check prompt format (after translations)
python check_prompt_format.py

# Backup prompt files
python backup_prompts.py

# Localization tools
python localize_agents_safe.py
python localize_terrain_only.py
```

## Git Commands
Standard git workflow for feature development:
```bash
git checkout -b feature/branch-name
git add <files>
git commit -m "message"
git push origin feature/branch-name
git checkout main
git merge feature/branch-name
```

## Key Parameters
- `--name`: Unique simulation identifier
- `--start`: Initial time format "YYYYMMDD-HH:MM"
- `--step`: Number of simulation steps
- `--stride`: Minutes per step (default: 10)
- `--resume`: Continue from checkpoint

## File Locations
- Configuration: `generative_agents/data/config.json`
- Prompts: `generative_agents/data/prompts/`
- Results: `generative_agents/results/`
- Agent data: `frontend/static/assets/village/agents/`