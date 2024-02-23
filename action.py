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
    end_line: int
    docstring: str | None
    definition: str


def get_diffs(diff_index: list[git.Diff]) -> list[Diff]:
    diffs = []
    for diff_item in diff_index:
        for diff_line in diff_item.diff.decode("utf-8").splitlines():
            if diff_line.startswith("@@"):
                file_a_line_info = diff_line.split(" ")[1]
                file_a_start_line, file_a_length = file_a_line_info[1:].split(",")
                file_a_start_line = int(file_a_start_line)
                file_a_length = int(file_a_length)
                file_a_end_line = file_a_start_line + file_a_length - 1
                file_b_line_info = diff_line.split(" ")[2]
                file_b_start_line, file_b_length = file_b_line_info[1:].split(",")
                file_b_start_line = int(file_b_start_line)
                file_b_length = int(file_b_length)
                file_b_end_line = file_b_start_line + file_b_length - 1
                diffs.append(
                    Diff(
                        file_a=FileDiff(
                            file_path=diff_item.a_path or diff_item.b_path,
                            start_line=file_a_start_line,
                            end_line=file_a_end_line,
                            diff=diff_item.diff.decode("utf-8"),
                        ),
                        file_b=FileDiff(
                            file_path=diff_item.b_path or diff_item.a_path,
                            start_line=file_b_start_line,
                            end_line=file_b_end_line,
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
                                        start_line=diff.file_b.start_line,
                                        end_line=diff.file_b.end_line,
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
        if doc.docstring is None:
            continue
        else:
            print(doc.docstring)
            files = pr.get_files()
            for file in files:
                if file.filename == doc.file:
                    file_sha = file.sha
                    break
            pr.create_issue_comment(
                f"""
The definition of [{doc.name}](https://github.com/{repo_name}/blob/{commit}/{doc.file}#L{doc.start_line}) in file **{doc.file}** has been modified and the corresponding docstring seems
to not be up to date regarding these changes.

If the docstring seems to be up to date, please ignore this message and resolve the issue.
"""
            )

        # print(doc.name)
        # print(doc.docstring)
        # print(doc.definition)
