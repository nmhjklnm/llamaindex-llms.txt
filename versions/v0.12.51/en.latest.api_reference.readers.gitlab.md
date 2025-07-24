# Gitlab
##  GitLabIssuesReader #
Bases: `BaseReader`
GitLab issues reader.
Source code in `llama-index-integrations/readers/llama-index-readers-gitlab/llama_index/readers/gitlab/issues/base.py`

| ```
class GitLabIssuesReader(BaseReader):
    """
    GitLab issues reader.
    """

    class IssueState(enum.Enum):
        """
        Issue type.

        Used to decide what issues to retrieve.

        Attributes:
            - OPEN: Issues that are open.
            - CLOSED: Issues that are closed.
            - ALL: All issues, open and closed.

        """

        OPEN = "opened"
        CLOSED = "closed"
        ALL = "all"

    class IssueType(enum.Enum):
        """
        Issue type.

        Used to decide what issues to retrieve.

        Attributes:
            - ISSUE: Issues.
            - INCIDENT: Incident.
            - TEST_CASE: Test case.
            - TASK: Task.

        """

        ISSUE = "issue"
        INCIDENT = "incident"
        TEST_CASE = "test_case"
        TASK = "task"

    class Scope(enum.Enum):
        """
        Scope.

        Used to determine the scope of the issue.

        Attributes:
            - CREATED_BY_ME: Issues created by the authenticated user.
            - ASSIGNED_TO_ME: Issues assigned to the authenticated user.
            - ALL: All issues.

        """

        CREATED_BY_ME = "created_by_me"
        ASSIGNED_TO_ME = "assigned_to_me"
        ALL = "all"

    def __init__(
        self,
        gitlab_client: gitlab.Gitlab,
        project_id: Optional[int] = None,
        group_id: Optional[int] = None,
        verbose: bool = False,
    ):
        super().__init__()

        self._gl = gitlab_client
        self._project_id = project_id
        self._group_id = group_id
        self._verbose = verbose

    def _build_document_from_issue(self, issue: GitLabIssue) -> Document:
        issue_dict = issue.asdict()
        title = issue_dict["title"]
        description = issue_dict["description"]
        document = Document(
            doc_id=str(issue_dict["iid"]),
            text=f"{title}\n{description}",
        )
        extra_info = {
            "state": issue_dict["state"],
            "labels": issue_dict["labels"],
            "created_at": issue_dict["created_at"],
            "closed_at": issue_dict["closed_at"],
            "url": issue_dict["_links"]["self"],  # API URL
            "source": issue_dict["web_url"],  # HTML URL, more convenient for humans
        }
        if issue_dict["assignee"]:
            extra_info["assignee"] = issue_dict["assignee"]["username"]
        if issue_dict["author"]:
            extra_info["author"] = issue_dict["author"]["username"]
        document.extra_info = extra_info
        return document

    def _get_project_issues(self, **kwargs):
        project = self._gl.projects.get(self._project_id)
        return project.issues.list(**kwargs)

    def _get_group_issues(self, **kwargs):
        group = self._gl.groups.get(self._group_id)
        return group.issues.list(**kwargs)

    def _to_gitlab_datetime_format(self, dt: Optional[datetime]) -> str:
        return dt.strftime("%Y-%m-%dT%H:%M:%S") if dt else None

    def load_data(
        self,
        assignee: Optional[Union[str, int]] = None,
        author: Optional[Union[str, int]] = None,
        confidential: Optional[bool] = None,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        iids: Optional[List[int]] = None,
        issue_type: Optional[IssueType] = None,
        labels: Optional[List[str]] = None,
        milestone: Optional[str] = None,
        non_archived: Optional[bool] = None,
        scope: Optional[Scope] = None,
        search: Optional[str] = None,
        state: Optional[IssueState] = IssueState.OPEN,
        updated_after: Optional[datetime] = None,
        updated_before: Optional[datetime] = None,
        **kwargs: Any,
    ) -> List[Document]:
        """
        Load group or project issues and converts them to documents. Please refer to the GitLab API documentation for the full list of parameters.

        Each issue is converted to a document by doing the following:

            - The doc_id of the document is the issue number.
            - The text of the document is the concatenation of the title and the description of the issue.
            - The extra_info of the document is a dictionary with the following keys:
                - state: State of the issue.
                - labels: List of labels of the issue.
                - created_at: Date when the issue was created.
                - closed_at: Date when the issue was closed. Only present if the issue is closed.
                - url: URL of the issue.
                - source: URL of the issue. More convenient for humans.
                - assignee: username of the user assigned to the issue. Only present if the issue is assigned.

        Args:
            - assignee: Username or ID of the user assigned to the issue.
            - author: Username or ID of the user that created the issue.
            - confidential: Filter confidential issues.
            - created_after: Filter issues created after the specified date.
            - created_before: Filter issues created before the specified date.
            - iids: Return only the issues having the given iid.
            - issue_type: Filter issues by type.
            - labels: List of label names, issues must have all labels to be returned.
            - milestone: The milestone title.
            - non_archived: Return issues from non archived projects.
            - scope: Return issues for the given scope.
            - search: Search issues against their title and description.
            - state: State of the issues to retrieve.
            - updated_after: Filter issues updated after the specified date.
            - updated_before: Filter issues updated before the specified date.


        Returns:
            List[Document]: List of documents.

        """
        to_gitlab_datetime_format = self._to_gitlab_datetime_format
        params = {
            "confidential": confidential,
            "created_after": to_gitlab_datetime_format(created_after),
            "created_before": to_gitlab_datetime_format(created_before),
            "iids": iids,
            "issue_type": issue_type.value if issue_type else None,
            "labels": labels,
            "milestone": milestone,
            "non_archived": non_archived,
            "scope": scope.value if scope else None,
            "search": search,
            "state": state.value if state else None,
            "updated_after": to_gitlab_datetime_format(updated_after),
            "updated_before": to_gitlab_datetime_format(updated_before),
        }

        if isinstance(assignee, str):
            params["assignee_username"] = assignee
        elif isinstance(assignee, int):
            params["assignee_id"] = assignee

        if isinstance(author, str):
            params["author_username"] = author
        elif isinstance(author, int):
            params["author_id"] = author

        filtered_params = {k: v for k, v in params.items() if v is not None}

        filtered_params.update(kwargs)

        issues = []

        if self._project_id:
            issues = self._get_project_issues(**filtered_params)
        if self._group_id:
            issues = self._get_group_issues(**filtered_params)

        return [self._build_document_from_issue(issue) for issue in issues]

```
  
---|---  
###  IssueState #
Bases: `Enum`
Issue type.
Used to decide what issues to retrieve.
Attributes:
Name | Type | Description  
---|---|---  
`-` |  `OPEN` |  Issues that are open.  
`-` |  `CLOSED` |  Issues that are closed.  
`-` |  `ALL` |  All issues, open and closed.  
Source code in `llama-index-integrations/readers/llama-index-readers-gitlab/llama_index/readers/gitlab/issues/base.py`

| ```
class IssueState(enum.Enum):
    """
    Issue type.

    Used to decide what issues to retrieve.

    Attributes:
        - OPEN: Issues that are open.
        - CLOSED: Issues that are closed.
        - ALL: All issues, open and closed.

    """

    OPEN = "opened"
    CLOSED = "closed"
    ALL = "all"

```
  
---|---  
###  IssueType #
Bases: `Enum`
Issue type.
Used to decide what issues to retrieve.
Attributes:
Name | Type | Description  
---|---|---  
`-` |  `ISSUE` |  Issues.  
`-` |  `INCIDENT` |  Incident.  
`-` |  `TEST_CASE` |  Test case.  
`-` |  `TASK` |  Task.  
Source code in `llama-index-integrations/readers/llama-index-readers-gitlab/llama_index/readers/gitlab/issues/base.py`

| ```
class IssueType(enum.Enum):
    """
    Issue type.

    Used to decide what issues to retrieve.

    Attributes:
        - ISSUE: Issues.
        - INCIDENT: Incident.
        - TEST_CASE: Test case.
        - TASK: Task.

    """

    ISSUE = "issue"
    INCIDENT = "incident"
    TEST_CASE = "test_case"
    TASK = "task"

```
  
---|---  
###  Scope #
Bases: `Enum`
Scope.
Used to determine the scope of the issue.
Attributes:
Name | Type | Description  
---|---|---  
`-` |  `CREATED_BY_ME` |  Issues created by the authenticated user.  
`-` |  `ASSIGNED_TO_ME` |  Issues assigned to the authenticated user.  
`-` |  `ALL` |  All issues.  
Source code in `llama-index-integrations/readers/llama-index-readers-gitlab/llama_index/readers/gitlab/issues/base.py`

| ```
class Scope(enum.Enum):
    """
    Scope.

    Used to determine the scope of the issue.

    Attributes:
        - CREATED_BY_ME: Issues created by the authenticated user.
        - ASSIGNED_TO_ME: Issues assigned to the authenticated user.
        - ALL: All issues.

    """

    CREATED_BY_ME = "created_by_me"
    ASSIGNED_TO_ME = "assigned_to_me"
    ALL = "all"

```
  
---|---  
###  load_data #
```
load_data(assignee: Optional[Union[str, int]] = None, author: Optional[Union[str, int]] = None, confidential: Optional[bool] = None, created_after: Optional[datetime] = None, created_before: Optional[datetime] = None, iids: Optional[List[int]] = None, issue_type: Optional[IssueType] = None, labels: Optional[List[str]] = None, milestone: Optional[str] = None, non_archived: Optional[bool] = None, scope: Optional[Scope] = None, search: Optional[str] = None, state: Optional[IssueState] = OPEN, updated_after: Optional[datetime] = None, updated_before: Optional[datetime] = None, **kwargs: Any) -> List[Document]

```

Load group or project issues and converts them to documents. Please refer to the GitLab API documentation for the full list of parameters.
Each issue is converted to a document by doing the following:
```
- The doc_id of the document is the issue number.
- The text of the document is the concatenation of the title and the description of the issue.
- The extra_info of the document is a dictionary with the following keys:
    - state: State of the issue.
    - labels: List of labels of the issue.
    - created_at: Date when the issue was created.
    - closed_at: Date when the issue was closed. Only present if the issue is closed.
    - url: URL of the issue.
    - source: URL of the issue. More convenient for humans.
    - assignee: username of the user assigned to the issue. Only present if the issue is assigned.

```

Parameters:
Name | Type | Description | Default  
---|---|---|---  
`-` |  `assignee` |  Username or ID of the user assigned to the issue. |  _required_  
`-` |  `author` |  Username or ID of the user that created the issue. |  _required_  
`-` |  `confidential` |  Filter confidential issues. |  _required_  
`-` |  `created_after` |  Filter issues created after the specified date. |  _required_  
`-` |  `created_before` |  Filter issues created before the specified date. |  _required_  
`-` |  `iids` |  Return only the issues having the given iid. |  _required_  
`-` |  `issue_type` |  Filter issues by type. |  _required_  
`-` |  `labels` |  List of label names, issues must have all labels to be returned. |  _required_  
`-` |  `milestone` |  The milestone title. |  _required_  
`-` |  `non_archived` |  Return issues from non archived projects. |  _required_  
`-` |  `scope` |  Return issues for the given scope. |  _required_  
`-` |  `search` |  Search issues against their title and description. |  _required_  
`-` |  `state` |  State of the issues to retrieve. |  _required_  
`-` |  `updated_after` |  Filter issues updated after the specified date. |  _required_  
`-` |  `updated_before` |  Filter issues updated before the specified date. |  _required_  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: List of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-gitlab/llama_index/readers/gitlab/issues/base.py`

| ```
def load_data(
    self,
    assignee: Optional[Union[str, int]] = None,
    author: Optional[Union[str, int]] = None,
    confidential: Optional[bool] = None,
    created_after: Optional[datetime] = None,
    created_before: Optional[datetime] = None,
    iids: Optional[List[int]] = None,
    issue_type: Optional[IssueType] = None,
    labels: Optional[List[str]] = None,
    milestone: Optional[str] = None,
    non_archived: Optional[bool] = None,
    scope: Optional[Scope] = None,
    search: Optional[str] = None,
    state: Optional[IssueState] = IssueState.OPEN,
    updated_after: Optional[datetime] = None,
    updated_before: Optional[datetime] = None,
    **kwargs: Any,
) -> List[Document]:
    """
    Load group or project issues and converts them to documents. Please refer to the GitLab API documentation for the full list of parameters.

    Each issue is converted to a document by doing the following:

        - The doc_id of the document is the issue number.
        - The text of the document is the concatenation of the title and the description of the issue.
        - The extra_info of the document is a dictionary with the following keys:
            - state: State of the issue.
            - labels: List of labels of the issue.
            - created_at: Date when the issue was created.
            - closed_at: Date when the issue was closed. Only present if the issue is closed.
            - url: URL of the issue.
            - source: URL of the issue. More convenient for humans.
            - assignee: username of the user assigned to the issue. Only present if the issue is assigned.

    Args:
        - assignee: Username or ID of the user assigned to the issue.
        - author: Username or ID of the user that created the issue.
        - confidential: Filter confidential issues.
        - created_after: Filter issues created after the specified date.
        - created_before: Filter issues created before the specified date.
        - iids: Return only the issues having the given iid.
        - issue_type: Filter issues by type.
        - labels: List of label names, issues must have all labels to be returned.
        - milestone: The milestone title.
        - non_archived: Return issues from non archived projects.
        - scope: Return issues for the given scope.
        - search: Search issues against their title and description.
        - state: State of the issues to retrieve.
        - updated_after: Filter issues updated after the specified date.
        - updated_before: Filter issues updated before the specified date.


    Returns:
        List[Document]: List of documents.

    """
    to_gitlab_datetime_format = self._to_gitlab_datetime_format
    params = {
        "confidential": confidential,
        "created_after": to_gitlab_datetime_format(created_after),
        "created_before": to_gitlab_datetime_format(created_before),
        "iids": iids,
        "issue_type": issue_type.value if issue_type else None,
        "labels": labels,
        "milestone": milestone,
        "non_archived": non_archived,
        "scope": scope.value if scope else None,
        "search": search,
        "state": state.value if state else None,
        "updated_after": to_gitlab_datetime_format(updated_after),
        "updated_before": to_gitlab_datetime_format(updated_before),
    }

    if isinstance(assignee, str):
        params["assignee_username"] = assignee
    elif isinstance(assignee, int):
        params["assignee_id"] = assignee

    if isinstance(author, str):
        params["author_username"] = author
    elif isinstance(author, int):
        params["author_id"] = author

    filtered_params = {k: v for k, v in params.items() if v is not None}

    filtered_params.update(kwargs)

    issues = []

    if self._project_id:
        issues = self._get_project_issues(**filtered_params)
    if self._group_id:
        issues = self._get_group_issues(**filtered_params)

    return [self._build_document_from_issue(issue) for issue in issues]

```
  
---|---  
##  GitLabRepositoryReader #
Bases: `BaseReader`
Source code in `llama-index-integrations/readers/llama-index-readers-gitlab/llama_index/readers/gitlab/repository/base.py`

| ```
class GitLabRepositoryReader(BaseReader):
    def __init__(
        self,
        gitlab_client: gitlab.Gitlab,
        project_id: int,
        use_parser: bool = False,
        verbose: bool = False,
    ):
        super().__init__()

        self._gl = gitlab_client
        self._use_parser = use_parser
        self._verbose = verbose
        self._project_url = f"{gitlab_client.api_url}/projects/{project_id}"

        self._project = gitlab_client.projects.get(project_id)

    def _parse_file_content(self, file_properties: dict, file_content: str) -> Document:
        raise NotImplementedError

    def _load_single_file(self, file_path: str, ref: Optional[str] = None) -> Document:
        file = self._project.files.get(file_path=file_path, ref=ref)
        file_properties = file.asdict()
        file_content = file.decode()

        if self._use_parser:
            return self._parse_file_content(file_properties, file_content)

        return Document(
            doc_id=file_properties["blob_id"],
            text=file_content,
            extra_info={
                "file_path": file_properties["file_path"],
                "file_name": file_properties["file_name"],
                "size": file_properties["size"],
                "url": f"{self._project_url}/projects/repository/files/{file_properties['file_path']}/raw",
            },
        )

    def load_data(
        self,
        ref: str,
        file_path: Optional[str] = None,
        path: Optional[str] = None,
        recursive: bool = False,
    ) -> List[Document]:
        """
        Load data from a GitLab repository.

        Args:
            ref: The name of a repository branch or commit id
            file_path: Path to the file to load.
            path: Path to the directory to load.
            recursive: Whether to load files recursively.

        Returns:
            List[Document]: List of documents loaded from the repository

        """
        if file_path:
            return [self._load_single_file(file_path, ref)]

        project = self._project

        params = {
            "ref": ref,
            "path": path,
            "recursive": recursive,
        }

        filtered_params = {k: v for k, v in params.items() if v is not None}

        repo_items = project.repository_tree(**filtered_params)

        documents = []

        for item in repo_items:
            if item["type"] == "blob":
                documents.append(self._load_single_file(item["path"], ref))

        return documents

```
  
---|---  
###  load_data #
```
load_data(ref: str, file_path: Optional[str] = None, path: Optional[str] = None, recursive: bool = False) -> List[Document]

```

Load data from a GitLab repository.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`ref` |  `str` |  The name of a repository branch or commit id |  _required_  
`file_path` |  `Optional[str]` |  Path to the file to load. |  `None`  
`path` |  `Optional[str]` |  Path to the directory to load. |  `None`  
`recursive` |  `bool` |  Whether to load files recursively. |  `False`  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: List of documents loaded from the repository  
Source code in `llama-index-integrations/readers/llama-index-readers-gitlab/llama_index/readers/gitlab/repository/base.py`

| ```
def load_data(
    self,
    ref: str,
    file_path: Optional[str] = None,
    path: Optional[str] = None,
    recursive: bool = False,
) -> List[Document]:
    """
    Load data from a GitLab repository.

    Args:
        ref: The name of a repository branch or commit id
        file_path: Path to the file to load.
        path: Path to the directory to load.
        recursive: Whether to load files recursively.

    Returns:
        List[Document]: List of documents loaded from the repository

    """
    if file_path:
        return [self._load_single_file(file_path, ref)]

    project = self._project

    params = {
        "ref": ref,
        "path": path,
        "recursive": recursive,
    }

    filtered_params = {k: v for k, v in params.items() if v is not None}

    repo_items = project.repository_tree(**filtered_params)

    documents = []

    for item in repo_items:
        if item["type"] == "blob":
            documents.append(self._load_single_file(item["path"], ref))

    return documents

```
  
---|---
