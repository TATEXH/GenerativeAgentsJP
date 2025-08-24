# Generative Agents JP - Project Overview

## Project Purpose
This is a Japanese localized version of a Chinese Generative Agents simulation - originally based on Stanford/Google's research project. It simulates a virtual world with 25 AI-powered agents that exhibit realistic human behavior patterns. The agents can autonomously organize parties, attend meetings, plan Valentine's Day activities, and demonstrate human-like living patterns.

The project is based on the "wounderland" refactored version of the original Generative Agents, with comprehensive Japanese localization including:
- All prompts translated from Chinese to Japanese
- Agent names localized to Japanese
- Location names translated to Japanese
- LLM output parsing adapted for Japanese language

## Tech Stack
- **Language**: Python 3.12
- **LLM Integration**: 
  - Ollama (local models) - default
  - OpenAI-compatible APIs - alternative
- **Vector Storage**: LlamaIndex for associative memory
- **Web Framework**: Flask for replay visualization
- **Configuration**: JSON-based configuration system

## Key Dependencies
- openai==1.98.0
- llama-index==0.13.0
- Flask==3.1.1
- Various LlamaIndex embedding providers (HuggingFace, Ollama, OpenAI)

## Architecture Overview
- **Core Modules**:
  - `agent.py`: AI agent with personality, memory, behavior systems
  - `game.py`: Orchestrates agent interactions and world simulation
  - `maze.py`: 2D tile-based world representation
  - `memory/`: Memory systems (associative, event, spatial, schedule)
  - `model/`: LLM integration layer
  - `prompt/`: Prompt template processing and output parsing
  - `utils/`: Utility functions including timer with Japanese weekdays

## Main Features
- 25 AI agents with distinct personalities
- Japanese language prompts and interactions
- Memory systems using vector embeddings
- Checkpoint/resume functionality
- Web-based replay system
- Support for both local (Ollama) and cloud LLM providers