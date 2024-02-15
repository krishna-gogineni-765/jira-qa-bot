from jira import JIRA

from src.brain.question_to_function import QuestionToFunction

temp_jira_url = 'https://jira.atlassian.com' # TODO : This needs to be updated per user's JIRA instance with their integration details
class JiraIntegration:
    def __init__(self, jira_url, auth_token=None):
        self.jira = JIRA(jira_url)

    def get_projects(self):
        projects = self.jira.projects()
        return [project.name for project in projects]

    def get_issue(self, issue_id):
        issue = self.jira.issue(issue_id)
        return issue

    def get_issues_by_project(self, project):
        issues = self.jira.search_issues(f'project={project}')
        return issues

    def get_issues_by_project_and_time(self, project, start_date, end_date):
        issues = self.jira.search_issues(f'project={project} and created >= {start_date} and created <= {end_date}')
        return issues

    def get_issues_by_assignee(self, project, assignee):
        issues = self.jira.search_issues(f'project={project} and assignee={assignee}')
        return issues

    def issues_to_df(self, issues):
        return issues.to_dataframe()


def fetch_projects() -> dict:
    jira = JIRA(temp_jira_url)
    projects = jira.projects()
    return {"projects": [project.name for project in projects]}


def fetch_issue(issue_id: str) -> dict:
    jira = JIRA(temp_jira_url)
    issue = jira.issue(issue_id)
    return {"issue": issue.raw}


def fetch_issues_by_project(project: str) -> dict:
    jira = JIRA(temp_jira_url)
    issues = jira.search_issues(f'project=\'{project}\'')
    return {"issues": [issue.raw for issue in issues]}


def fetch_issues_by_project_and_time(project: str, start_date: str, end_date: str) -> dict:
    jira = JIRA(temp_jira_url)
    issues = jira.search_issues(f'project=\'{project}\' and created >= \'{start_date}\' and created <= \'{end_date}\'')
    return {"issues": [issue.raw for issue in issues]}

function_name_to_function_map = {
    "fetch_projects": fetch_projects,
    "fetch_issue": fetch_issue,
    "fetch_issues_by_project": fetch_issues_by_project,
    "fetch_issues_by_project_and_time": fetch_issues_by_project_and_time
}

