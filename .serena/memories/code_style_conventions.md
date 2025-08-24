# Code Style and Conventions

## General Python Conventions
- Python 3.12+ syntax
- UTF-8 encoding with `# -*- coding: utf-8 -*-` headers
- Use pathlib.Path for file operations
- Exception handling with try/catch blocks

## Project-Specific Patterns

### File Structure
- Configuration centralized in JSON files
- Template-based prompt system for maintainability
- Modular architecture with clear separation of concerns

### Localization Patterns
- Japanese text used throughout (agent names, prompts, locations)
- Consistent format preservation during translation
- Placeholder patterns: `${variable}` format in templates
- Structured output format: `<object>: description` with colons

### LLM Integration
- Provider abstraction (Ollama/OpenAI compatible)
- Robust parsing with fallback patterns
- Debug logging for LLM output parsing failures
- Template-based prompt generation

### Memory System
- Vector-based storage using LlamaIndex
- Retention parameters for memory management
- Structured data storage with JSON serialization

### Error Handling
- Graceful degradation for LLM parsing failures
- Comprehensive logging for debugging
- Backup systems for safe file operations

## Naming Conventions
- Japanese agent names (hiragana): あいか, あきこ, etc.
- File naming: snake_case for Python files
- Class naming: PascalCase
- Variable naming: snake_case
- Constants: UPPER_CASE

## Import Organization
Standard Python import order:
1. Standard library
2. Third-party packages (openai, llama-index, flask)
3. Local modules (relative imports)

## Documentation
- Docstrings in Japanese when appropriate
- Code comments explaining complex logic
- Configuration documentation in Japanese
- README files with usage examples