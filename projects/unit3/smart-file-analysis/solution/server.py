#!/usr/bin/env python3
"""
Module 2: Smart File Analysis with Resources
An enhanced MCP server that provides Resources for project context and intelligent file analysis.
"""

import json
import os
import subprocess
from typing import Dict, List, Any, Optional
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Initialize the FastMCP server
mcp = FastMCP("pr-agent")

# PR template directory
TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"

# Team guidelines directory for resources
TEAM_GUIDELINES_DIR = Path(__file__).parent.parent.parent / "team-guidelines"


@mcp.tool()
async def analyze_file_changes(
    base_branch: str = "main",
    include_diff: bool = True
) -> str:
    """Get the full diff and list of changed files in the current git repository.
    
    Args:
        base_branch: Base branch to compare against (default: main)
        include_diff: Include the full diff content (default: true)
    """
    try:
        # Get list of changed files
        files_result = subprocess.run(
            ["git", "diff", "--name-status", f"{base_branch}...HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Get diff statistics
        stat_result = subprocess.run(
            ["git", "diff", "--stat", f"{base_branch}...HEAD"],
            capture_output=True,
            text=True
        )
        
        # Get the actual diff if requested
        diff_content = ""
        if include_diff:
            diff_result = subprocess.run(
                ["git", "diff", f"{base_branch}...HEAD"],
                capture_output=True,
                text=True
            )
            diff_content = diff_result.stdout
        
        # Get commit messages for context
        commits_result = subprocess.run(
            ["git", "log", "--oneline", f"{base_branch}..HEAD"],
            capture_output=True,
            text=True
        )
        
        analysis = {
            "base_branch": base_branch,
            "files_changed": files_result.stdout,
            "statistics": stat_result.stdout,
            "commits": commits_result.stdout,
            "diff": diff_content if include_diff else "Diff not included (set include_diff=true to see full diff)"
        }
        
        return json.dumps(analysis, indent=2)
        
    except subprocess.CalledProcessError as e:
        return f"Error analyzing changes: {e.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def get_pr_templates() -> str:
    """List available PR templates with their content."""
    templates = []
    
    # Define default templates
    default_templates = {
        "bug.md": "Bug Fix",
        "feature.md": "Feature",
        "docs.md": "Documentation",
        "refactor.md": "Refactor",
        "test.md": "Test",
        "performance.md": "Performance",
        "security.md": "Security"
    }
    
    for filename, template_type in default_templates.items():
        template_path = TEMPLATES_DIR / filename
        
        # Read template content
        content = template_path.read_text()
        
        templates.append({
            "filename": filename,
            "type": template_type,
            "content": content
        })
    
    return json.dumps(templates, indent=2)


@mcp.tool()
async def suggest_template(changes_summary: str, change_type: str) -> str:
    """Let Claude analyze the changes and suggest the most appropriate PR template.
    
    Args:
        changes_summary: Your analysis of what the changes do
        change_type: The type of change you've identified (bug, feature, docs, refactor, test, etc.)
    """
    
    # Get available templates
    templates_response = await get_pr_templates()
    templates = json.loads(templates_response)
    
    # Map change types to template files
    type_mapping = {
        "bug": "bug.md",
        "fix": "bug.md",
        "feature": "feature.md",
        "enhancement": "feature.md",
        "docs": "docs.md",
        "documentation": "docs.md",
        "refactor": "refactor.md",
        "cleanup": "refactor.md",
        "test": "test.md",
        "testing": "test.md",
        "performance": "performance.md",
        "optimization": "performance.md",
        "security": "security.md"
    }
    
    # Find matching template
    template_file = type_mapping.get(change_type.lower(), "feature.md")
    selected_template = next(
        (t for t in templates if t["filename"] == template_file),
        templates[0]  # Default to first template if no match
    )
    
    suggestion = {
        "recommended_template": selected_template,
        "reasoning": f"Based on your analysis: '{changes_summary}', this appears to be a {change_type} change.",
        "template_content": selected_template["content"],
        "usage_hint": "Claude can help you fill out this template based on the specific changes in your PR."
    }
    
    return json.dumps(suggestion, indent=2)


# Resources for project context
@mcp.resource("file://templates/{filename}")
async def read_template(filename: str) -> str:
    """Read a specific PR template file.
    
    Args:
        filename: The template filename (e.g., 'bug.md', 'feature.md')
    """
    template_path = TEMPLATES_DIR / filename
    if not template_path.exists():
        return f"Template {filename} not found"
    
    content = template_path.read_text()
    return content


@mcp.resource("file://team-guidelines/{filename}")
async def read_team_guidelines(filename: str) -> str:
    """Read team-specific guideline files like coding standards, PR guidelines, etc.
    
    Args:
        filename: The guideline filename (e.g., 'coding-standards.md', 'pr-guidelines.md')
    """
    guideline_path = TEAM_GUIDELINES_DIR / filename
    if not guideline_path.exists():
        return f"Guideline file {filename} not found"
    
    content = guideline_path.read_text()
    return content


@mcp.resource("git://recent-changes")
async def get_recent_changes() -> str:
    """Get recent commit history to understand project patterns."""
    try:
        # Get last 20 commits with more detail
        result = subprocess.run(
            ["git", "log", "--pretty=format:%h|%an|%ae|%ad|%s", "-20", "--date=short"],
            capture_output=True,
            text=True,
            check=True
        )
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('|')
                if len(parts) >= 5:
                    commits.append({
                        "hash": parts[0],
                        "author": parts[1],
                        "email": parts[2],
                        "date": parts[3],
                        "message": parts[4]
                    })
        
        # Get file change statistics
        stats_result = subprocess.run(
            ["git", "log", "--stat", "--oneline", "-10"],
            capture_output=True,
            text=True
        )
        
        return json.dumps({
            "recent_commits": commits,
            "change_statistics": stats_result.stdout,
            "total_commits": len(commits)
        }, indent=2)
        
    except subprocess.CalledProcessError as e:
        return json.dumps({"error": f"Git error: {e.stderr}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.resource("team://review-process")
async def get_team_review_process() -> str:
    """Get team-specific review process and requirements."""
    process = {
        "pr_size_limits": {
            "small": "< 100 lines: 1 reviewer",
            "medium": "100-500 lines: 2 reviewers",
            "large": "> 500 lines: Split into smaller PRs or schedule review meeting"
        },
        "review_sla": {
            "critical": "Within 2 hours",
            "high": "Within 4 hours",
            "normal": "Within 1 business day",
            "low": "Within 2 business days"
        },
        "merge_requirements": {
            "ci_status": "All checks must pass",
            "approvals": "Required based on PR size",
            "conflicts": "Must be resolved before merge",
            "documentation": "Update if API changes"
        },
        "communication": {
            "slack_channel": "#pull-requests",
            "urgent_prefix": "@here",
            "review_request": "Please review: {pr_link}",
            "merge_notification": "Merged: {pr_title}"
        }
    }
    
    return json.dumps(process, indent=2)


if __name__ == "__main__":
    mcp.run()