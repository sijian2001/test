# Task Completion Checklist

## When Starting a Task
1. Change task status to "In Progress"
2. Set task start date/time (including time)
3. Create branch from develop: `feature/<task_id>`
4. Create empty commit: `chore: start feature/<task_id>`
5. Create draft PR:
   ```bash
   gh pr create --assignee @me --base develop --draft
   ```
   - Title: `【<task_id>】<title>`
   - Body: Include Notion task link
6. Create implementation plan
7. Communicate plan to user

## During Development
- Run tests frequently: `python -m pytest tests/ -v`
- Test specific components as needed
- Use formatter to maintain code readability
- Update `.tmp/task.md` with progress (if applicable)

## Before Completing a Task
1. **Run all tests**:
   ```bash
   python -m pytest tests/ -v
   ```
2. **Verify no errors** in implementation
3. **Do NOT commit** - ask for user confirmation first

## When Completing a Task
1. Set PR status to ready
2. Merge PR:
   ```bash
   gh pr merge --merge --auto --delete-branch
   ```
3. Set task completion date/time (including time)
4. Add "Summary" to task
   - Review command history and context
   - Create retrospective text
   - Notion heading: "振り返り"
5. Change task status to "Completed"
6. Return prompt to user

## Testing Strategy
- Comprehensive unit tests with pytest
- Mock-based testing for repositories and services
- Test coverage for all layers (batch, business, domain)
- Separate tests for test1 and test2 database components