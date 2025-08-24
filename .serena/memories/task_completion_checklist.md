# Task Completion Checklist

## Before Committing Changes

### Code Quality Checks
1. **Environment Activation**: Ensure conda environment is activated
   ```bash
   source /root/miniconda3/etc/profile.d/conda.sh && conda activate generative_agents_cn
   ```

2. **Format Validation**: For prompt translations, run format checker
   ```bash
   python check_prompt_format.py
   ```

3. **Functional Testing**: Test core functionality
   ```bash
   cd generative_agents
   python start.py --name test-sim --start "20250213-09:30" --step 1
   ```

### Japanese Localization Specific
- Verify placeholder preservation: `${variable}` patterns intact
- Check structured output formats: `<object>: description` with colons
- Ensure parsing patterns match prompt output formats
- Validate Japanese text consistency (no Chinese remnants)

### Git Operations
1. **Check Status**
   ```bash
   git status
   git diff --name-only
   ```

2. **Stage Changes**
   ```bash
   git add <relevant-files>
   ```

3. **Commit with Descriptive Message**
   ```bash
   git commit -m "descriptive message with 🤖 Generated with Claude Code footer"
   ```

4. **Push and Merge** (when requested)
   ```bash
   git push origin <branch-name>
   git checkout main
   git merge <branch-name>
   ```

## No Linting/Testing Commands
- This project does not have specific linting or testing commands configured
- Manual functional testing is the primary validation method
- Format checking tools are project-specific (like `check_prompt_format.py`)

## File Backup Strategy
- Create backups before major changes: `backup_prompts.py`
- Use timestamped backup directories
- Verify backup integrity before proceeding with modifications

## Error Resolution Process
1. Check LLM output parsing logs for format mismatches
2. Update prompt templates to enforce expected output formats
3. Modify parsing patterns in `modules/prompt/scratch.py`
4. Test with actual LLM to verify fixes
5. Document format requirements clearly in prompts