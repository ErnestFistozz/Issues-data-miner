import requests
import time
from common import CommonAttributes
from utils import Utils
import asyncio
import httpx
from aiolimiter import AsyncLimiter
from dataclasses import dataclass, asdict
from typing import Optional

HEADERS = ['repository', 'issue_id', 'issue_number', 'labels', 'status', 'comments',
           'created_at', 'updatdataclassesed_at', 'closed_at', 'issue_title', 'state_reason', 'assigned',
           'number_of_assignees']

@dataclass
class IssueFilters:
    per_page: Optional[int] = 100
    page: int = 1
    state: Optional[str] = 'all'
    direction: Optional[str] = 'asc'

class IssueMiner(CommonAttributes):
    def __init__(self, org: str, repo: str) -> None:
        super().__init__(org, repo)

    def get_issues(self) -> None:
        page = 1
        wait_time = 3600
        issues = []
        directory = Utils.determine_directory()
        filename = '{}{}'.format(directory, "github_issues.csv")
        while True:
            search_query = IssueFilters(
                page=page
            )
            url = f"https://api.github.com/repos/{self.organisation}/{self.repository}/issues"
            response = requests.get(url, params=search_query)
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

    async def request_github_issues_async(self, client, url, search_query, limiter):
        async with limiter:
            response = await client.get(url, params=search_query)
            if not response.json():
                return []

            if response.status_code in [403, 429]:
                time.sleep(300)
                response = await client.get(url, params=search_query)
            try:
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
                    for issue in response.json()
                ]
                return page_issues
            except KeyError:
                return []

    async def issues_data_async(self):
        rate_limit = AsyncLimiter(300, 0.1)
        async with httpx.AsyncClient() as client:
            issues = []
            page = 1
            has_issues = True
            while has_issues:
                search_query = IssueFilters(page=page)
                url = f"https://api.github.com/repos/{self.organisation}/{self.repository}/issues"
                current_page = await self.request_github_issues_async(client, url, asdict(search_query), rate_limit)
                if not current_page:
                    has_issues = False
                issues.extend(current_page)
                await asyncio.sleep(5)
                page += 1
        return issues
