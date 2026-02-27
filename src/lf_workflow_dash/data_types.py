from dataclasses import dataclass, field
from datetime import datetime
from typing import List

import pytz
import yaml


def calculate_statistics(all_projects):
    """Calculate aggregate statistics across all projects.
    
    Args:
        all_projects (list): List of ProjectData objects
        
    Returns:
        dict: Dictionary containing statistics
    """
    passing_count = 0
    failing_count = 0
    stale_count = 0
    pending_count = 0
    total_workflows = 0
    
    for project in all_projects:
        # Check all workflow types
        workflows = []
        if project.smoke_test:
            workflows.append(project.smoke_test)
        if project.build_docs:
            workflows.append(project.build_docs)
        if project.benchmarks:
            workflows.append(project.benchmarks)
        if project.live_build:
            workflows.append(project.live_build)
        workflows.extend(project.other_workflows)
        
        project_passing = 0
        project_failing = 0
        
        for workflow in workflows:
            total_workflows += 1
            if workflow.workflow_status == "success":
                passing_count += 1
                project_passing += 1
            elif workflow.workflow_status == "failure":
                failing_count += 1
                project_failing += 1
            elif workflow.workflow_status == "pending":
                pending_count += 1
            
            if workflow.is_stale:
                stale_count += 1
        
        # Store per-project statistics
        project.passing_workflows = project_passing
        project.failing_workflows = project_failing
    
    passing_percent = round((passing_count / total_workflows * 100) if total_workflows > 0 else 0, 1)
    failing_percent = round((failing_count / total_workflows * 100) if total_workflows > 0 else 0, 1)
    
    return {
        "passing_count": passing_count,
        "failing_count": failing_count,
        "stale_count": stale_count,
        "pending_count": pending_count,
        "total_workflows": total_workflows,
        "passing_percent": passing_percent,
        "failing_percent": failing_percent,
        "repo_count": len(all_projects)
    }


@dataclass
class WorkflowElemData:
    """Per-workflow information"""

    workflow_name: str = ""
    workflow_url: str = ""
    workflow_status: str = ""
    display_class: str = ""
    icon_class: str = ""
    owner: str = ""
    repo: str = ""
    conclusion_time: str = ""
    conclusion_time_one_line: str = ""
    is_stale: bool = False
    friendly_name: str = ""
    branch: str = ""

    def __init__(self, workflow_name, repo_url, owner, repo, branch=""):
        self.workflow_name = workflow_name
        self.owner = owner
        self.repo = repo
        self.workflow_url = f"{repo_url}/actions/workflows/{self.workflow_name}"
        self.workflow_status = "pending"
        self.display_class = "yellow-cell"
        self.icon_class = "fa-solid fa-circle-question"
        self.branch = branch

    def set_status(self, status, conclusion_time, is_stale):
        """Set the completion status of a workflow. This will also update the display class
        to suit the warning level.

        Args:
            status (str): how the workflow completed (e.g. "success" or "failure")
            conclusion_time (str): pretty print of the conclusion of the last workflow run
            is_stale (bool): if True, the last workflow run was a long time ago
        """
        self.workflow_status = status
        self.conclusion_time = conclusion_time
        self.conclusion_time_one_line = conclusion_time.replace("<br>", " ")
        self.is_stale = is_stale
        if status == "success":
            self.display_class = "green-cell"
            self.icon_class = "fa-solid fa-circle-check"
        elif status == "failure":
            self.display_class = "red-cell"
            self.icon_class = "fa-solid fa-circle-xmark"


@dataclass
class ProjectData:
    """Per-repo project workflow data"""

    owner: str = ""
    repo: str = ""
    icon: str = ""
    repo_url: str = ""
    copier_version: str = ""
    copier_version_display_class: str = "yellow-cell"
    
    # Per-project workflow counts for charts
    passing_workflows: int = 0
    failing_workflows: int = 0

    smoke_test: WorkflowElemData = None
    build_docs: WorkflowElemData = None
    benchmarks: WorkflowElemData = None
    live_build: WorkflowElemData = None

    other_workflows: List[WorkflowElemData] = field(default_factory=list)

    def __post_init__(self):
        self.repo_url = f"https://github.com/{self.owner}/{self.repo}"

    def set_copier_version(self, this_version, template_version):
        """Set the copier template version used in this project.
        This will also update the display class to suit if this project's version
        matches the copier template version.

        Args:
            this_version (semver.Version): version of this project
            template_version (semver.Version): version of the copier template project
        """
        if not this_version:
            return
        self.copier_version = str(this_version)
        if this_version < template_version:
            self.copier_version_display_class = "yellow-cell"
        elif this_version == template_version:
            self.copier_version_display_class = "green-cell"
        else:
            self.copier_version_display_class = "red-cell"


def read_yaml_file(file_path):
    """Read data from a YAML file and return a tuple with page title and a list of repository tuples.

    Parameters
    ----------
    file_path : str
        Path to the YAML file.

    Returns
    -------
    tuple
        A tuple containing the page title (str) and a list of tuples containing ('owner', 'repo', 'workflow').
    """
    with open(file_path, "r", encoding="utf8") as yaml_file:
        data = yaml.safe_load(yaml_file)

    # Get the page_title if it exists, otherwise set it to None
    page_title = data.get("page_title", None)
    extra_links = data.get("extra_links", [])
    copier_project = data.get("copier_project", "lincc-frameworks/python-project-template")

    repos = data.get("repos", [])
    all_projects = []
    contains_other = False
    contains_smoke = False
    contains_bench = False
    contains_docs = False
    contains_live = False
    for item in repos:
        owner = item["owner"]
        repo = item["repo"]
        project_data = ProjectData(owner=owner, repo=repo)

        if "smoke-test" in item:
            project_data.smoke_test = WorkflowElemData(
                item["smoke-test"], repo_url=project_data.repo_url, owner=owner, repo=repo
            )
            contains_smoke = True
        if "build-docs" in item:
            project_data.build_docs = WorkflowElemData(
                item["build-docs"], repo_url=project_data.repo_url, owner=owner, repo=repo
            )
            contains_docs = True
        if "benchmarks" in item:
            project_data.benchmarks = WorkflowElemData(
                item["benchmarks"], repo_url=project_data.repo_url, owner=owner, repo=repo
            )
            contains_bench = True
        if "live-build" in item:
            project_data.live_build = WorkflowElemData(
                item["live-build"],
                repo_url=project_data.repo_url,
                owner=owner,
                repo=repo,
                branch="main",
            )
            contains_live = True
        if "other_workflows" in item:
            for name in item["other_workflows"]:
                project_data.other_workflows.append(
                    WorkflowElemData(name, repo_url=project_data.repo_url, owner=owner, repo=repo)
                )
            contains_other = True

        all_projects.append(project_data)

    timezone = pytz.timezone("America/New_York")
    last_updated = datetime.now(timezone).strftime("%H:%M %B %d, %Y (US-NYC)")

    return {
        "page_title": page_title,
        "all_projects": all_projects,
        "contains_other": contains_other,
        "contains_smoke": contains_smoke,
        "contains_docs": contains_docs,
        "contains_bench": contains_bench,
        "contains_live": contains_live,
        "dash_name": "LINCC Frameworks Builds",
        "dash_repo": "lf-workflow-dash",
        "last_updated": last_updated,
        "extra_links": extra_links,
        "copier_project": copier_project,
    }
