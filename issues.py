import requests
import time
from common import CommonAttributes
from utils import Utils

HEADERS = ['repository', 'issue_id', 'issue_number', 'labels', 'status', 'comments',
           'created_at', 'updated_at', 'closed_at', 'issue_title', 'state_reason', 'assigned', 'number_of_assignees']


class IssueMiner(CommonAttributes):
    def __init__(self, org: str, repo: str, per_page=100) -> None:
        super().__init__(org, repo)
        self.per_page = per_page

    def get_issues(self) -> None:
        page = 1
        wait_time = 3600
        issues = []
        directory = Utils.determine_directory()
        filename = '{}{}'.format(directory, "github_issues.csv")
        while True:
            url = f"https://api.github.com/repos/{self.organisation}/{self.repository}/issues?per_page={self.per_page}&page={page}&state=all&direction=asc"
            response = requests.get(url)
            if response.status_code != 200:
                if response.status_code in [403, 429]:
                    time.sleep(wait_time)
                    response = requests.get(url)
                    continue
                else:
                    break
            json_data = response.json()
            if not json_data:
                break
            page_issues = [
                {
                    "repository": f"{self.organisation}/{self.repository}",
                    "issue_id": issue['id'],
                    "issue_number": issue['number'],
                    "labels": "" if not issue['labels'] else ",".join([label['name'] for label in issue['labels']]),
                    "status": issue['state'],
                    "comments": int(issue['comments']),
                    "created_at": issue['created_at'],
                    "updated_at": issue['updated_at'],
                    "closed_at": issue['closed_at'],
                    "issue_title": issue['title'],
                    "state_reason": issue['state_reason'],
                    "assigned": False if not issue['assignee'] else True,
                    "number_of_assignees": 0 if not issue['assignee'] else len(issue['assignee']),
                }
                for issue in json_data
            ]
            issues.extend(page_issues)
            page += 1
            # call method to save to file
            Utils.write_to_file(filename, HEADERS, issues)
            time.sleep(10)
