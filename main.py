from comments import CommentsMiner
from issues import IssueMiner
from releases import ReleaseMiner
from utils import Utils

if __name__ == '__main__':
    repositories = Utils.read_file('repositories.txt')
    for repository in repositories:
        # Mining Issues
        issues = IssueMiner(repository[0], repositories[1])
        issues.get_issues()

        # Mining Comments
        comments = CommentsMiner(repository[0], repositories[1])
        comments.get_comments()

        # Mining Releases
        releases = ReleaseMiner(repository[0], repositories[1])
        releases.get_releases()