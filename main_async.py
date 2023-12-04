from issues import IssueMiner
from utils import Utils
import asyncio

FILE_HEADERS = ['repository', 'issue_id', 'issue_number', 'labels', 'status', 'comments',
                'created_at', 'updated_at', 'closed_at', 'issue_title', 'state_reason', 'assigned',
                'number_of_assignees']

if __name__ == '__main__':
    repositories = Utils.read_file('test_repo.txt')
    directory = Utils.determine_directory()
    filename = '{}{}'.format(directory, "github_issues_async.csv")
    for repository in repositories:
        issues = IssueMiner(repository[0], repository[1])
        results = asyncio.run(issues.issues_data_async())
        Utils.write_to_file(filename, FILE_HEADERS, results)
