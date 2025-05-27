# Manual Testing Guide for Module 2 Solution

## Prerequisites

1. Ensure you're in a git repository with commit history
2. Install uv following instructions at: https://docs.astral.sh/uv/getting-started/installation/
3. Install dependencies:
   ```bash
   uv sync --all-extras
   ```

## Test 1: Verify Resources Setup

Check that the shared directories exist:
```bash
# From the solution directory
ls ../../templates/
ls ../../team-guidelines/
```

You should see:
- Templates: bug.md, feature.md, docs.md, etc.
- Team guidelines: coding-standards.md, pr-guidelines.md

## Test 2: Test with Claude

1. **Configure MCP Settings**
   
   Add to your Claude Desktop MCP settings (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):
   
   ```json
   {
     "mcpServers": {
       "pr-agent": {
         "command": "uv",
         "args": [
           "--directory",
           "/absolute/path/to/smart-file-analysis/solution",
           "run",
           "server.py"
         ]
       }
     }
   }
   ```

2. **Import to Claude Code** ([documentation](https://docs.anthropic.com/en/docs/claude-code/tutorials#import-mcp-servers-from-claude-desktop)):
   ```bash
   claude mcp import-from-desktop
   ```

3. **Restart Claude Desktop/Code** to pick up the new server

4. **Test Resource Access**
   
   Ask Claude to test the new resources:
   - "What are our team's coding standards?"
   - "Show me the PR guidelines"
   - "What are the recent commits in this repository?"
   - "What's our team's review process?"
   - "Can you read the bug.md template?"

## Test 3: Combined Tool and Resource Usage

Test how Claude uses both tools and resources together:

1. **Make some changes in your repo**:
   ```bash
   echo "# New feature" >> feature.py
   git add feature.py
   ```

2. **Ask Claude for comprehensive help**:
   - "Can you analyze my changes and suggest a PR based on our team guidelines?"
   - "What template should I use given our coding standards?"
   - "Based on recent commits, does my change follow the project patterns?"

## Expected Behavior

### Resources Should Return:

1. **read_template("filename.md")**
   - Full content of the template file
   - Error message if file not found

2. **read_team_guidelines("filename.md")**
   - Content of the guideline file
   - Error message if file not found

3. **get_recent_changes()**
   - JSON with recent_commits array
   - Each commit has: hash, author, email, date, message
   - Includes change_statistics

4. **get_team_review_process()**
   - JSON with pr_size_limits, review_sla, merge_requirements, communication

### Claude Should Be Able To:

1. **Access team context** when making suggestions
2. **Reference specific guidelines** in responses
3. **Analyze commit patterns** to suggest consistent changes
4. **Apply team processes** when recommending workflows

## Troubleshooting

- **"File not found"**: Check that team-guidelines and templates directories exist at the correct path
- **Resources not showing in Claude**: Ensure the server restarted after adding resources
- **Git errors**: Make sure you're in a git repository with commit history
- **Path issues**: Verify TEAM_GUIDELINES_DIR and TEMPLATES_DIR point to correct locations

## Integration Testing

Test that Module 2 builds on Module 1:

1. All Module 1 tools should still work
2. Resources should enhance tool suggestions
3. Claude should reference guidelines when analyzing changes

Example test:
- "Analyze my changes and suggest a template that follows our team guidelines"

This should use:
- `analyze_file_changes` tool (from Module 1)
- `read_team_guidelines` resource (new in Module 2)
- `suggest_template` tool with context from resources