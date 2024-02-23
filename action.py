import os
import git
import ast
from pydantic import BaseModel
from github import Github, Commit


class FileDiff(BaseModel):
    """
    Add a docstring
    """

    file_path: str
    start_line: int
    end_line: int
    diff: str


class Diff(BaseModel):
    file_a: FileDiff
    file_b: FileDiff


class DocumentedDefinition(BaseModel):
    file: str
    name: str
    start_line: int
    docstring: str | None
    definition: str


def get_diffs(diff_index: list[git.Diff]) -> list[Diff]:
    diffs = []
    for diff_item in diff_index:
        for diff_line in diff_item.diff.decode("utf-8").splitlines():
            if diff_line.startswith("@@"):
                # Extract the start line number and the length of changes in the new file
                line_info = diff_line.split(" ")[2]  # Gets the '+start2,len2' part
                start_line, length = line_info[1:].split(
                    ","
                )  # Remove the '+' and split start2 and len2

                # Convert start_line and length to integers
                start_line = int(start_line)
                length = int(length)

                # Calculate the end line number
                end_line = (
                    start_line + length - 1
                )  # Subtract 1 since start_line is included
                diffs.append(
                    Diff(
                        file_a=FileDiff(
                            file_path=diff_item.a_path,
                            start_line=start_line,
                            end_line=end_line,
                            diff=diff_item.diff.decode("utf-8"),
                        ),
                        file_b=FileDiff(
                            file_path=diff_item.b_path,
                            start_line=start_line,
                            end_line=end_line,
                            diff=diff_item.diff.decode("utf-8"),
                        ),
                    )
                )
    return diffs


def get_modified_functions_diff(repo_path, pr_branch, base_branch):
    repo = git.Repo(repo_path)
    pr_commit = None
    base_commit = None
    for ref in repo.remotes.origin.refs:
        if ref.remote_head == pr_branch:
            pr_commit = ref.commit
        elif ref.remote_head == base_branch:
            base_commit = ref.commit
    if pr_commit is None or base_commit is None:
        raise ValueError("Branch not found")

    diffs = get_diffs(base_commit.diff(pr_commit, paths="*.py", create_patch=True))
    docs = extract_docstring_from_diffs(diffs)

    # for diff in diffs:
    #     if diff.a_blob in _diffs:
    #         print(diff)
    #         modified_functions.extend(diff.diff.decode("utf-8").split("\n"))
    # file_path = diff.b_path  # Path to the modified file
    # patch = diff.diff.decode("utf-8")  # Diff patch text
    # modified_functions.extend(extract_functions_from_patch(file_path, patch))

    return pr_commit, docs


def extract_docstring_from_diffs(diffs: list[Diff]) -> list[DocumentedDefinition]:
    """
    Test Toto
    """

    docs = []
    for file_path in {diff.file_a.file_path for diff in diffs}:
        with open(file_path, "r") as file:
            code = file.read()
            tree = ast.parse(code)
            for f in ast.walk(tree):
                if isinstance(f, ast.FunctionDef) or isinstance(f, ast.ClassDef):
                    for diff in diffs:
                        if diff.file_a.file_path == file_path:
                            if (
                                f.lineno >= diff.file_a.start_line
                                and f.lineno <= diff.file_a.end_line
                            ) or (
                                f.end_lineno >= diff.file_a.start_line
                                and f.end_lineno <= diff.file_a.end_line
                            ):
                                docs.append(
                                    DocumentedDefinition(
                                        file=file_path,
                                        name=f.name,
                                        start_line=f.lineno,
                                        docstring=ast.get_docstring(f),
                                        definition=ast.unparse(f),
                                    )
                                )
                                break
    return docs


def get_docstring(function_code):
    # Parse the function code using ast.parse
    # Extract and return the docstring if present
    pass


# Main execution
if __name__ == "__main__":
    repo_path = "."
    pr_branch = os.environ.get("PR_BRANCH")
    base_branch = os.environ.get("BASE_BRANCH")
    github_token = os.environ.get("GITHUB_TOKEN")
    repository_name = os.environ.get("REPOSITORY_NAME")
    pr_number = int(os.environ.get("PR_NUMBER"))
    commit, docs = get_modified_functions_diff(
        repo_path,
        pr_branch,
        base_branch,
    )
    g = Github(github_token)
    repo_name = repository_name
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    for doc in docs:
        print(doc.file)
        print(doc.name)
        print(doc.docstring)
        print(doc.start_line)

        pr.create_review_comment(
            "test",
            commit=pr.get_commits().reversed[0],
            path=doc.file,
            line=doc.start_line,
        )
        # print(doc.name)
        # print(doc.docstring)
        # print(doc.definition)
