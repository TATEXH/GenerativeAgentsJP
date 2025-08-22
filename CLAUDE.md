# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Chinese localized implementation of Generative Agents - a virtual world simulation with 25 AI-powered agents that simulate realistic human behavior. The project is based on the Stanford/Google Generative Agents research but rebuilt with better engineering practices and Chinese language support.

## Core Architecture

### Main Components

- **Agent System** (`modules/agent.py`): Core AI agent with personality, memory, and behavior systems
- **Game Engine** (`modules/game.py`): Orchestrates agent interactions and world simulation  
- **Maze/World** (`modules/maze.py`): 2D tile-based world representation with collision detection
- **Memory Systems** (`modules/memory/`): 
  - `associate.py`: Vector-based associative memory using LlamaIndex
  - `event.py`: Event memory storage and retrieval
  - `spatial.py`: Location-based memory
  - `schedule.py`: Daily planning and task scheduling
- **LLM Integration** (`modules/model/llm_model.py`): Supports both Ollama and OpenAI-compatible APIs
- **Prompt Templates** (`data/prompts/`): All Chinese prompt templates for agent behaviors

### Configuration

All configuration is centralized in `generative_agents/data/config.json`:
- LLM provider settings (Ollama or OpenAI-compatible)
- Embedding model configuration
- Agent behavior parameters (perception range, memory retention, etc.)

### Data Flow

1. Agents perceive their environment through vision radius and attention bandwidth
2. LLM processes perceptions using Chinese prompts to generate actions/dialogue
3. Memory systems store experiences using vector embeddings
4. Game engine updates world state and agent positions
5. Results are checkpointed for replay functionality

## Important: Conda Environment

**ALWAYS activate the conda environment before running any Python commands:**
```bash
source /root/miniconda3/etc/profile.d/conda.sh && conda activate generative_agents_cn
```

This project requires the `generative_agents_cn` conda environment which has all necessary dependencies installed.

## Common Commands

### Environment Setup
```bash
# Create conda environment
conda create -n generative_agents_cn python=3.12
conda activate generative_agents_cn

# Install dependencies
pip install -r requirements.txt
```

### Running Simulation
```bash
# ALWAYS activate conda environment first
source /root/miniconda3/etc/profile.d/conda.sh && conda activate generative_agents_cn
cd generative_agents

# Start new simulation
python start.py --name sim-test --start "20250213-09:30" --step 10 --stride 10

# Resume from checkpoint
python start.py --name sim-test --resume --step 10 --stride 10
```

### Data Processing and Replay

#### Step 1: Compress Simulation Data
```bash
# ALWAYS activate conda environment first
source /root/miniconda3/etc/profile.d/conda.sh && conda activate generative_agents_cn
cd generative_agents

# Generate replay data (required before viewing replay)
python compress.py --name <simulation-name>
# Example: python compress.py --name long-sim
```

#### Step 2: Start Replay Server
```bash
# ALWAYS activate conda environment first  
source /root/miniconda3/etc/profile.d/conda.sh && conda activate generative_agents_cn

# Start replay server (runs on port 5000)
python replay.py
```

#### Step 3: Access Replay in Browser
Open browser and navigate to:
- `http://127.0.0.1:5000/?name=<simulation-name>`
- Example: `http://127.0.0.1:5000/?name=long-sim`

Available simulations after compression:
- Check `generative_agents/results/compressed/` for available replays
- Each simulation needs to be compressed before it can be replayed

### Key Parameters
- `--name`: Unique simulation identifier for checkpointing
- `--start`: Initial simulation time (format: "YYYYMMDD-HH:MM") 
- `--step`: Number of simulation steps to run
- `--stride`: Minutes per simulation step (default: 10)
- `--resume`: Continue from last checkpoint

## Development Notes

### LLM Configuration
- Default: Uses Ollama with local models (qwen3:8b, bge-m3 embeddings)
- Alternative: Set `provider: "openai"` for OpenAI-compatible APIs
- Models must support Chinese language for proper agent behavior

### Adding New Agents
- Agent personas defined in `start.py` personas list (Chinese names)
- Agent data stored in `frontend/static/assets/village/agents/`
- Each agent needs: `agent.json`, `portrait.png`, `texture.png`

### Checkpoint System
- Simulation state saved every step to `results/checkpoints/{name}/`
- Agent memory persisted using LlamaIndex storage
- Conversation logs stored in `conversation.json`
- Use `--resume` flag to continue from last checkpoint

### Memory System
- Uses LlamaIndex for vector storage and retrieval
- Embedding models configurable (Ollama or OpenAI)
- Memory retention controlled by `associate.retention` parameter
- Spatial memory tracks agent locations and interactions

### Prompt Engineering
- All prompts in `data/prompts/` directory
- Templates use Chinese language optimized for local models
- Key prompts: daily scheduling, conversation, reflection, action planning
- Handles special model outputs (e.g., <think> tags from newer models)

## File Structure Notes

- `frontend/`: Flask web interface for replay visualization
- `results/`: Generated simulation data and checkpoints
- `modules/`: Core simulation logic organized by functionality
- Configuration and prompts separated from code for easy modification