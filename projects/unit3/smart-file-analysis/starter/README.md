# Module 2: Smart File Analysis - Starter Code

Welcome to Module 2! In this module, you'll enhance your PR Agent with MCP Resources.

## Your Task

The starter code includes all Module 1 tools. Your job is to add Resources that provide project context to Claude.

## Resources to Implement

1. **Template Resource** (`file://templates/{filename}`)
   - Allow Claude to read individual PR template files
   
2. **Team Guidelines** (`file://team-guidelines/{filename}`)
   - Expose coding standards and PR guidelines
   
3. **Git History** (`git://recent-changes`)
   - Provide recent commit patterns
   
4. **Team Review Process** (`team://review-process`)
   - Share team review requirements and SLAs

## Getting Started

1. Install dependencies:
   ```bash
   uv sync --all-extras
   ```

2. Review the shared team guidelines:
   ```bash
   ls ../../../team-guidelines/
   # You'll see: coding-standards.md, pr-guidelines.md
   ```

3. Implement the TODOs in `server.py`

4. Test your implementation with Claude

## Resources vs Tools

Remember:
- **Tools** perform actions (may have side effects)
- **Resources** provide read-only data access

## File Locations

- Templates: `../../../templates/`
- Team Guidelines: `../../../team-guidelines/`
- Your server: `server.py`

## Need Help?

- Check the implementation hints in the code comments
- Review the Module 2 documentation
- Compare with the solution when you're done