import requests
import time
from common import CommonAttributes
from utils import Utils

HEADERS = ['repository', 'name', 'release_id', 'tag_name', 'target_commitish', 'created_at', 'updated_at', 'draft', 'prerelease']

class ReleaseMiner(CommonAttributes):
    def __init__(self, org: str, repo: str, per_page=100) -> None:
        super().__init__(org, repo)
        self.per_page = per_page

    def get_releases(self) -> None:
        page = 1
        wait_time = 3600
        releases = []
        directory = Utils.determine_directory()
        filename = '{}{}'.format(directory, "github_releases.csv")
        while True:
            url = f"https://api.github.com/repos/{self.organisation}/{self.repository}/releases?per_page={self.per_page}&page={page}"
            response = requests.get(url)
            if response.status_code != 200:
                if response.status_code in [403, 429]:
                    time.sleep(wait_time)
                    continue
                else:
                    break
            json_data = response.json()
            if not json_data:
                break
            page_releases = [
                    {
                            "repository": f"{self.organisation}/{self.repository}",
                            "name": release['state'],
                            "release_id": release['id'],
                            "tag_name": release['tag_name'],
                            "target_commitish": release['target_commitish'],
                            "created_at": release['created_at'],
                            "updated_at": release['updated_at'],
                            "draft": release['draft'],
                            "prerelease": release['prerelease'],
                    }
                    for release in json_data
                ]
            releases.extend(page_releases)
            Utils.write_to_file(filename, HEADERS, releases)
            page += 1
            time.sleep(10)
