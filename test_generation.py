#!/usr/bin/env python3
"""
Quick test to verify dashboard generation works with the new design.
Run this locally to test: python test_generation.py
"""

from lf_workflow_dash.data_types import ProjectData, WorkflowElemData, calculate_statistics, read_yaml_file
from lf_workflow_dash.update_dashboard import update_html

# Create sample data
all_projects = []

# Project 1: All passing
p1 = ProjectData(owner="test-org", repo="repo1")
p1.smoke_test = WorkflowElemData("smoke.yml", "https://github.com/test-org/repo1", "test-org", "repo1")
p1.smoke_test.set_status("success", "1 hour ago", False)
p1.build_docs = WorkflowElemData("docs.yml", "https://github.com/test-org/repo1", "test-org", "repo1")
p1.build_docs.set_status("success", "2 hours ago", False)
p1.copier_version = "0.3.0"
p1.copier_version_display_class = "green-cell"
all_projects.append(p1)

# Project 2: Some failing
p2 = ProjectData(owner="test-org", repo="repo2")
p2.smoke_test = WorkflowElemData("smoke.yml", "https://github.com/test-org/repo2", "test-org", "repo2")
p2.smoke_test.set_status("failure", "30 minutes ago", False)
p2.build_docs = WorkflowElemData("docs.yml", "https://github.com/test-org/repo2", "test-org", "repo2")
p2.build_docs.set_status("success", "1 hour ago", False)
p2.copier_version = "0.2.8"
p2.copier_version_display_class = "yellow-cell"
all_projects.append(p2)

# Calculate statistics
stats = calculate_statistics(all_projects)

# Create context
context = {
    "page_title": "Test Dashboard",
    "all_projects": all_projects,
    "stats": stats,
    "contains_smoke": True,
    "contains_docs": True,
    "contains_bench": False,
    "contains_live": False,
    "contains_other": False,
    "dash_repo": "lf-workflow-dash",
    "last_updated": "18:00 February 27, 2026 (US-NYC)",
    "extra_links": [],
    "copier_semver": "0.3.0"
}

# Generate HTML
print("Generating test dashboard...")
update_html("test_output.html", context)
print(f"✓ Dashboard generated successfully: test_output.html")
print(f"\n📊 Statistics:")
print(f"  Passing: {stats['passing_count']} ({stats['passing_percent']}%)")
print(f"  Failing: {stats['failing_count']} ({stats['failing_percent']}%)")
print(f"  Total workflows: {stats['total_workflows']}")
print(f"  Repositories: {stats['repo_count']}")
print(f"\nOpen test_output.html in your browser to verify the enhanced design!")
