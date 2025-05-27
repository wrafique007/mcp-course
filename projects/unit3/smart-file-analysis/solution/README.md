# Module 2: Smart File Analysis - Solution

This is the complete solution for Module 2, which enhances the PR Agent with MCP Resources.

## What's New in Module 2

Building on Module 1's tools, this solution adds:

1. **Resources** for exposing project context to Claude
2. **Dynamic URI patterns** for accessing specific files
3. **Team-specific guidelines** that help Claude make better decisions

## Key Resources Implemented

- `file://templates/{filename}` - Read individual PR templates
- `file://team-guidelines/{filename}` - Access coding standards and PR guidelines
- `git://recent-changes` - Analyze recent commit patterns
- `team://review-process` - Understand team review requirements

## Running the Solution

```bash
# Install dependencies
uv sync --all-extras

# Run the server
uv run server.py
```

## Testing

Configure in Claude Code:
```bash
# Add the MCP server
claude mcp add pr-agent "uv" "--directory" "/path/to/smart-file-analysis/solution" "run" "server.py"

# Verify configuration
claude mcp list
```

## Project Structure

```
solution/
├── server.py              # MCP server with Tools and Resources
├── pyproject.toml        # Dependencies
└── README.md            # This file

Shared resources:
../../../team-guidelines/  # Team coding standards and PR guidelines
../../../templates/        # PR templates
```

## Key Improvements from Module 1

1. **Context Awareness**: Claude can now read team guidelines to understand your specific requirements
2. **Git History**: Claude can analyze recent commits to understand project patterns
3. **Resource URIs**: Clean, intuitive paths for accessing different types of data