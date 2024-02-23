import git
from ast import parse, FunctionDef


def get_modified_functions_diff(repo_path, pr_branch, base_branch="main"):
    repo = git.Repo(repo_path)
    base_commit = repo.commit(base_branch)
    pr_commit = repo.commit(pr_branch)

    diffs = base_commit.diff(pr_commit, paths="*.py", create_patch=True)
    modified_functions = []

    for diff in diffs:
        if diff.change_type in ["A", "M"]:  # Added or Modified files
            file_path = diff.b_path  # Path to the modified file
            patch = diff.diff.decode("utf-8")  # Diff patch text
            modified_functions.extend(extract_functions_from_patch(file_path, patch))

    return modified_functions


def extract_functions_from_patch(file_path, patch_text):
    # Logic to parse the patch text, identify function edits, and extract those functions
    # You may need to use regular expressions or other parsing methods to extract the edited lines/functions
    pass


def get_docstring(function_code):
    # Parse the function code using ast.parse
    # Extract and return the docstring if present
    pass


# Main execution
if __name__ == "__main__":
    repo_path = "https://github.com/mde-pach/test_github_action"
    pr_branch = ""
    modified_functions = get_modified_functions_diff(repo_path, pr_branch)
    for func in modified_functions:
        print(get_docstring(func))
