#!/usr/bin/env python3
"""
Quick test script to verify the enhanced dashboard functionality.
This can be used to test the statistics calculation without needing a GitHub token.
"""

from lf_workflow_dash.data_types import ProjectData, WorkflowElemData, calculate_statistics


def test_statistics_calculation():
    """Test the calculate_statistics function with sample data."""
    
    # Create sample projects
    projects = []
    
    # Project 1: All passing
    p1 = ProjectData(owner="test-org", repo="repo1")
    p1.smoke_test = WorkflowElemData("smoke.yml", "https://github.com/test-org/repo1", "test-org", "repo1")
    p1.smoke_test.set_status("success", "1 hour ago", False)
    p1.build_docs = WorkflowElemData("docs.yml", "https://github.com/test-org/repo1", "test-org", "repo1")
    p1.build_docs.set_status("success", "2 hours ago", False)
    projects.append(p1)
    
    # Project 2: Mixed status
    p2 = ProjectData(owner="test-org", repo="repo2")
    p2.smoke_test = WorkflowElemData("smoke.yml", "https://github.com/test-org/repo2", "test-org", "repo2")
    p2.smoke_test.set_status("failure", "30 minutes ago", False)
    p2.build_docs = WorkflowElemData("docs.yml", "https://github.com/test-org/repo2", "test-org", "repo2")
    p2.build_docs.set_status("success", "1 day ago", True)  # Stale
    projects.append(p2)
    
    # Project 3: Pending
    p3 = ProjectData(owner="test-org", repo="repo3")
    p3.smoke_test = WorkflowElemData("smoke.yml", "https://github.com/test-org/repo3", "test-org", "repo3")
    # Use default pending status
    projects.append(p3)
    
    # Calculate statistics
    stats = calculate_statistics(projects)
    
    # Print results
    print("=" * 60)
    print("DASHBOARD STATISTICS TEST")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"  Total Repositories: {stats['repo_count']}")
    print(f"  Total Workflows: {stats['total_workflows']}")
    print(f"\n✅ Passing: {stats['passing_count']} ({stats['passing_percent']}%)")
    print(f"❌ Failing: {stats['failing_count']} ({stats['failing_percent']}%)")
    print(f"⏰ Stale: {stats['stale_count']}")
    print(f"⏳ Pending: {stats['pending_count']}")
    
    print(f"\n📦 Per-Repository Breakdown:")
    for project in projects:
        print(f"  {project.repo}:")
        print(f"    Passing: {project.passing_workflows}")
        print(f"    Failing: {project.failing_workflows}")
    
    print("\n" + "=" * 60)
    print("✓ Statistics calculation working correctly!")
    print("=" * 60)
    
    # Verify expected values
    assert stats['repo_count'] == 3
    assert stats['passing_count'] == 3
    assert stats['failing_count'] == 1
    assert stats['stale_count'] == 1
    assert stats['pending_count'] == 1
    assert stats['total_workflows'] == 5
    
    return True


if __name__ == "__main__":
    try:
        test_statistics_calculation()
        print("\n✅ All tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
