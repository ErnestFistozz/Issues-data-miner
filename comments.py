import requests
import time
from common import CommonAttributes
from utils import Utils

HEADERS = ['repository', 'issue_id', 'comment_id', 'created_at', 'updated_at', 'comment_msg']
class CommentsMiner(CommonAttributes):
    def __init__(self, org: str, repo: str, per_page=100) -> None:
        super().__init__(org, repo)
        self.per_page = per_page

    def get_comments(self) -> None:
        page = 1
        wait_time = 3600
        comments = []
        directory = Utils.determine_directory()
        filename = '{}{}'.format(directory, "github_comments.csv")
        while True:
            url = f"https://api.github.com/repos/{self.organisation}/{self.repository}/issues/comments?per_page={self.per_page}&page={page}&direction=asc"
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
            page_comments = [
                {
                    "repository": f"{self.organisation}/{self.repository}",
                    "issue_id": comment['issue_url'].split('/')[-1],
                    "comment_id": comment['id'],
                    "created_at": comment['created_at'],
                    "updated_at": comment['updated_at'],
                    "comment_msg": comment['body']
                }
                for comment in json_data
            ]
            comments.extend(page_comments)
            Utils.write_to_file(filename, HEADERS, comments)
            page += 1
            time.sleep(10)
