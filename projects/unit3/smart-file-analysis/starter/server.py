#!/usr/bin/env python3
"""
Module 2: Smart File Analysis - Starter Code
TODO: Enhance your MCP server with Resources for project context

This starter code includes the Module 1 solution as a foundation.
Your task is to add Resources that provide project context to help Claude make better decisions.
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
# NOTE: For this exercise, we're hardcoding the path to keep things simple.
# In production, this would typically come from configuration or environment variables.
TEAM_GUIDELINES_DIR = Path(__file__).parent.parent.parent / "team-guidelines"


# ===== Module 1 Tools (Already Implemented) =====

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


# ===== Module 2: Add Resources Below =====
# Resources provide contextual information that helps Claude make better decisions.
# Unlike Tools (which perform actions), Resources expose data for Claude to read.

# TODO: Implement a resource for individual PR templates
# @mcp.resource("file://templates/{filename}")
# async def read_template(filename: str) -> str:
#     """Read a specific PR template file.
#     
#     Args:
#         filename: The template filename (e.g., 'bug.md', 'feature.md')
#     """
#     # Your implementation here
#     pass


# TODO: Implement a resource for team guideline files
# @mcp.resource("file://team-guidelines/{filename}")
# async def read_team_guidelines(filename: str) -> str:
#     """Read team-specific guideline files like coding standards, PR guidelines, etc.
#     
#     Args:
#         filename: The guideline filename (e.g., 'coding-standards.md', 'pr-guidelines.md')
#     """
#     # Your implementation here
#     # Hint: Read from TEAM_GUIDELINES_DIR / filename
#     pass


# TODO: Implement a resource for recent git history
# @mcp.resource("git://recent-changes")
# async def get_recent_changes() -> str:
#     """Get recent commit history to understand project patterns."""
#     # Your implementation here
#     # Hint: Use git log with formatting to get structured commit data
#     pass


# TODO: Implement a resource for team review process
# @mcp.resource("team://review-process")
# async def get_team_review_process() -> str:
#     """Get team-specific review process and requirements."""
#     # Your implementation here
#     # Hint: Return a JSON structure with PR size limits, review SLAs, etc.
#     pass


if __name__ == "__main__":
    mcp.run()