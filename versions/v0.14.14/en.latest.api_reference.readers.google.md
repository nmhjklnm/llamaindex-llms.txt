# Google
##  GmailReader #
Bases: `BaseReader`, `BaseModel`
Gmail reader.
Reads emails
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`max_results` |  `int` |  Defaults to 10. |  _required_  
`query` |  `str` |  Gmail query. Defaults to None. |  _required_  
`service` |  `Any` |  Gmail service. Defaults to None. |  _required_  
`results_per_page` |  `Optional[int]` |  Max number of results per page. Defaults to 10. |  _required_  
`use_iterative_parser` |  `bool` |  Use iterative parser. Defaults to False. |  _required_  
Source code in `llama-index-integrations/readers/llama-index-readers-google/llama_index/readers/google/gmail/base.py`

| ```
class GmailReader(BaseReader, BaseModel):
    """
    Gmail reader.

    Reads emails

    Args:
        max_results (int): Defaults to 10.
        query (str): Gmail query. Defaults to None.
        service (Any): Gmail service. Defaults to None.
        results_per_page (Optional[int]): Max number of results per page. Defaults to 10.
        use_iterative_parser (bool): Use iterative parser. Defaults to False.

    """

    query: str = None
    use_iterative_parser: bool = False
    max_results: int = 10
    service: Any
    results_per_page: Optional[int]

    def load_data(self) -> List[Document]:
        """Load emails from the user's account."""
        from googleapiclient.discovery import build

        credentials = self._get_credentials()
        if not self.service:
            self.service = build("gmail", "v1", credentials=credentials)

        messages = self.search_messages()

        results = []
        for message in messages:
            text = message.pop("body")
            extra_info = message
            results.append(Document(text=text, extra_info=extra_info or {}))

        return results

    def _get_credentials(self) -> Any:
        """
        Get valid user credentials from storage.

        The file token.json stores the user's access and refresh tokens, and is
        created automatically when the authorization flow completes for the first
        time.

        Returns:
            Credentials, the obtained credential.

        """
        import os

        from google_auth_oauthlib.flow import InstalledAppFlow

        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials

        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=8080)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        return creds

    def search_messages(self):
        query = self.query

        max_results = self.max_results
        if self.results_per_page:
            max_results = self.results_per_page

        results = (
            self.service.users()
            .messages()
            .list(userId="me", q=query, maxResults=int(max_results))
            .execute()
        )
        messages = results.get("messages", [])

        if len(messages) < self.max_results:
            # paginate if there are more results
            while "nextPageToken" in results:
                page_token = results["nextPageToken"]
                results = (
                    self.service.users()
                    .messages()
                    .list(
                        userId="me",
                        q=query,
                        pageToken=page_token,
                        maxResults=int(max_results),
                    )
                    .execute()
                )
                messages.extend(results["messages"])
                if len(messages) >= self.max_results:
                    break

        result = []
        try:
            for message in messages:
                message_data = self.get_message_data(message)
                if not message_data:
                    continue
                result.append(message_data)
        except Exception as e:
            raise Exception("Can't get message data" + str(e))

        return result

    def get_message_data(self, message):
        message_id = message["id"]
        message_data = (
            self.service.users()
            .messages()
            .get(format="raw", userId="me", id=message_id)
            .execute()
        )
        if self.use_iterative_parser:
            body = self.extract_message_body_iterative(message_data)
        else:
            body = self.extract_message_body(message_data)

        if not body:
            return None

        # https://developers.google.com/gmail/api/reference/rest/v1/users.messages
        return {
            "id": message_data["id"],
            "threadId": message_data["threadId"],
            "snippet": message_data["snippet"],
            "internalDate": message_data["internalDate"],
            "body": body,
        }

    def extract_message_body_iterative(self, message: dict):
        if message["raw"]:
            body = base64.urlsafe_b64decode(message["raw"].encode("utf-8"))
            mime_msg = email.message_from_bytes(body)
        else:
            mime_msg = message

        body_text = ""
        if mime_msg.get_content_type() == "text/plain":
            plain_text = mime_msg.get_payload(decode=True)
            charset = mime_msg.get_content_charset("utf-8")
            body_text = plain_text.decode(charset).encode("utf-8").decode("utf-8")

        elif mime_msg.get_content_maintype() == "multipart":
            msg_parts = mime_msg.get_payload()
            for msg_part in msg_parts:
                body_text += self.extract_message_body_iterative(msg_part)

        return body_text

    def extract_message_body(self, message: dict):
        from bs4 import BeautifulSoup

        try:
            body = base64.urlsafe_b64decode(message["raw"].encode("utf-8"))
            mime_msg = email.message_from_bytes(body)

            # If the message body contains HTML, parse it with BeautifulSoup
            if "text/html" in mime_msg:
                soup = BeautifulSoup(body, "html.parser")
                body = soup.get_text()
            return body.decode("utf-8")
        except Exception as e:
            raise Exception("Can't parse message body" + str(e))

```
  
---|---  
###  load_data #
```
load_data() -> List[Document]

```

Load emails from the user's account.
Source code in `llama-index-integrations/readers/llama-index-readers-google/llama_index/readers/google/gmail/base.py`

| ```
def load_data(self) -> List[Document]:
    """Load emails from the user's account."""
    from googleapiclient.discovery import build

    credentials = self._get_credentials()
    if not self.service:
        self.service = build("gmail", "v1", credentials=credentials)

    messages = self.search_messages()

    results = []
    for message in messages:
        text = message.pop("body")
        extra_info = message
        results.append(Document(text=text, extra_info=extra_info or {}))

    return results

```
  
---|---  
##  GoogleCalendarReader #
Bases: `BaseReader`
Google Calendar reader.
Reads events from Google Calendar
Source code in `llama-index-integrations/readers/llama-index-readers-google/llama_index/readers/google/calendar/base.py`

| ```
class GoogleCalendarReader(BaseReader):
    """
    Google Calendar reader.

    Reads events from Google Calendar

    """

    def load_data(
        self,
        number_of_results: Optional[int] = 100,
        start_date: Optional[Union[str, datetime.date]] = None,
    ) -> List[Document]:
        """
        Load data from user's calendar.

        Args:
            number_of_results (Optional[int]): the number of events to return. Defaults to 100.
            start_date (Optional[Union[str, datetime.date]]): the start date to return events from. Defaults to today.

        """
        from googleapiclient.discovery import build

        credentials = self._get_credentials()
        service = build("calendar", "v3", credentials=credentials)

        if start_date is None:
            start_date = datetime.date.today()
        elif isinstance(start_date, str):
            start_date = datetime.date.fromisoformat(start_date)

        start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
        start_datetime_utc = start_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=start_datetime_utc,
                maxResults=number_of_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])

        if not events:
            return []

        results = []
        for event in events:
            if "dateTime" in event["start"]:
                start_time = event["start"]["dateTime"]
            else:
                start_time = event["start"]["date"]

            if "dateTime" in event["end"]:
                end_time = event["end"]["dateTime"]
            else:
                end_time = event["end"]["date"]

            event_string = f"Status: {event['status']}, "
            event_string += f"Summary: {event['summary']}, "
            event_string += f"Start time: {start_time}, "
            event_string += f"End time: {end_time}, "

            organizer = event.get("organizer", {})
            display_name = organizer.get("displayName", "N/A")
            email = organizer.get("email", "N/A")
            if display_name != "N/A":
                event_string += f"Organizer: {display_name} ({email})"
            else:
                event_string += f"Organizer: {email}"

            results.append(Document(text=event_string))

        return results

    def _get_credentials(self) -> Any:
        """
        Get valid user credentials from storage.

        The file token.json stores the user's access and refresh tokens, and is
        created automatically when the authorization flow completes for the first
        time.

        Returns:
            Credentials, the obtained credential.

        """
        from google_auth_oauthlib.flow import InstalledAppFlow

        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials

        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        return creds

```
  
---|---  
###  load_data #
```
load_data(number_of_results: Optional[int] = 100, start_date: Optional[Union[str, date]] = None) -> List[Document]

```

Load data from user's calendar.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`number_of_results` |  `Optional[int]` |  the number of events to return. Defaults to 100. |  `100`  
`start_date` |  `Optional[Union[str, date]]` |  the start date to return events from. Defaults to today. |  `None`  
Source code in `llama-index-integrations/readers/llama-index-readers-google/llama_index/readers/google/calendar/base.py`

| ```
def load_data(
    self,
    number_of_results: Optional[int] = 100,
    start_date: Optional[Union[str, datetime.date]] = None,
) -> List[Document]:
    """
    Load data from user's calendar.

    Args:
        number_of_results (Optional[int]): the number of events to return. Defaults to 100.
        start_date (Optional[Union[str, datetime.date]]): the start date to return events from. Defaults to today.

    """
    from googleapiclient.discovery import build

    credentials = self._get_credentials()
    service = build("calendar", "v3", credentials=credentials)

    if start_date is None:
        start_date = datetime.date.today()
    elif isinstance(start_date, str):
        start_date = datetime.date.fromisoformat(start_date)

    start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
    start_datetime_utc = start_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start_datetime_utc,
            maxResults=number_of_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = events_result.get("items", [])

    if not events:
        return []

    results = []
    for event in events:
        if "dateTime" in event["start"]:
            start_time = event["start"]["dateTime"]
        else:
            start_time = event["start"]["date"]

        if "dateTime" in event["end"]:
            end_time = event["end"]["dateTime"]
        else:
            end_time = event["end"]["date"]

        event_string = f"Status: {event['status']}, "
        event_string += f"Summary: {event['summary']}, "
        event_string += f"Start time: {start_time}, "
        event_string += f"End time: {end_time}, "

        organizer = event.get("organizer", {})
        display_name = organizer.get("displayName", "N/A")
        email = organizer.get("email", "N/A")
        if display_name != "N/A":
            event_string += f"Organizer: {display_name} ({email})"
        else:
            event_string += f"Organizer: {email}"

        results.append(Document(text=event_string))

    return results

```
  
---|---  
##  GoogleChatReader #
Bases: `BasePydanticReader`
Google Chat Reader.
Reads messages from Google Chat
Source code in `llama-index-integrations/readers/llama-index-readers-google/llama_index/readers/google/chat/base.py`

| ```
class GoogleChatReader(BasePydanticReader):
    """
    Google Chat Reader.

    Reads messages from Google Chat
    """

    is_remote: bool = True

    @classmethod
    def class_name(cls) -> str:
        """Gets name identifier of class."""
        return "GoogleChatReader"

    def load_data(
        self,
        space_names: List[str],
        num_messages: int = -1,
        after: datetime = None,
        before: datetime = None,
        order_asc: bool = True,
    ) -> List[Document]:
        """
        Loads documents from Google Chat.

        Args:
            space_name (List[str]): List of Space ID names found at top of URL (without the "space/").
            num_messages (int, optional): Number of messages to load (may exceed this number). If -1, then loads all messages. Defaults to -1.
            after (datetime, optional): Only search for messages after this datetime (UTC). Defaults to None.
            before (datetime, optional): Only search for messages before this datetime (UTC). Defaults to None.
            order_asc (bool, optional): If messages should be ordered by ascending time order. Defaults to True.

        Returns:
            List[Document]: List of document objects

        """
        from googleapiclient.discovery import build

        # get credentials and create chat service
        credentials = self._get_credentials()
        service = build("chat", "v1", credentials=credentials)

        logger.info("Credentials successfully obtained.")

        res = []
        for space_name in space_names:
            all_msgs = self._get_msgs(
                service, space_name, num_messages, after, before, order_asc
            )  # gets raw API output in list of dict
            msgs_sorted = self._sort_msgs(
                space_name, all_msgs
            )  # puts messages into list of Document objects
            res.extend(msgs_sorted)
            logger.info(f"Successfully retrieved messages from {space_name}")

        return res

    def _sort_msgs(self, space_name: str, all_msgs: List[Dict[str, Any]]) -> Document:
        """
        Sorts messages from space and puts them into Document.

        Args:
            space_name (str): Space ID
            all_msgs (List[Dict[str, Any]]): All messages
            order_asc (bool): If ordered by ascending order

        Returns:
            Document: Document with messages

        """
        res = []
        id_to_text = self._id_to_text(
            all_msgs
        )  # maps message ID to text (useful for retrieving info about quote replies)
        thread_msg_cnt = self._get_thread_msg_cnt(
            all_msgs
        )  # gets message count in each thread
        for msg in all_msgs:
            if any(
                i not in msg for i in ("name", "text", "thread", "sender", "createTime")
            ):
                # invalid message
                continue

            if "name" not in msg["thread"] or "name" not in msg["sender"]:
                # invalid message
                continue

            metadata = {
                "space_id": space_name,
                "sender_id": msg["sender"]["name"],
                "timestamp": msg["createTime"],
            }

            if (
                "quotedMessageMetadata" in msg
                and msg["quotedMessageMetadata"]["name"] in id_to_text
            ):
                # metadata for a quote reply
                metadata["quoted_msg"] = id_to_text[
                    msg["quotedMessageMetadata"]["name"]
                ]

            # adds metadata for threads
            # all threads with a message count of 1 gets counted as the "main thread"
            thread_id = msg["thread"]["name"]
            if thread_msg_cnt[thread_id] > 1:
                metadata["thread_id"] = thread_id
            else:
                metadata["thread_id"] = "Main Thread"

            doc = Document(id_=msg["name"], text=msg["text"], metadata=metadata)
            res.append(doc)

        return res

    def _id_to_text(self, all_msgs: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Maps message ID to text, used for quote replies.

        Args:
            all_msgs (List[Dict[str, Any]]): All messages

        Returns:
            Dict[str, str]: Map message ID -> message text

        """
        res = {}

        for msg in all_msgs:
            if "text" not in msg or "name" not in msg:
                continue

            res[msg["name"]] = msg["text"]

        return res

    def _get_thread_msg_cnt(self, all_msgs: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Gets message count for each thread ID.

        Args:
            all_msgs (List[Dict[str, Any]]): All messages

        Returns:
            Dict[str, int]: Maps thread ID -> count of messages that were in that thread

        """
        # maps thread ID -> count
        threads_dict = {}
        for msg in all_msgs:
            thread_name = msg["thread"]["name"]
            if thread_name not in threads_dict:
                # add thread name to dict
                threads_dict[thread_name] = 1
            else:
                threads_dict[thread_name] += 1

        return threads_dict

    def _get_msgs(
        self,
        service: Any,
        space_name: str,
        num_messages: int = -1,
        after: datetime = None,
        before: datetime = None,
        order_asc: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Puts raw API output of chat messages from one space into a list.

        Args:
            service (Any): Google Chat API service object
            space_name (str): Space ID name found at top of URL (without the "space/").
            num_messages (int, optional): Number of messages to load (may exceed this number). If -1, then loads all messages. Defaults to -1.
            after (datetime, optional): Only search for messages after this datetime (UTC). Defaults to None.
            before (datetime, optional): Only search for messages before this datetime (UTC). Defaults to None.
            order_asc (bool, optional): If messages should be ordered by ascending time order. Defaults to True.

        Returns:
            List[Dict[str, Any]]: List of message objects

        """
        all_msgs = []

        # API parameters
        parent = f"spaces/{space_name}"
        page_token = ""
        filter_str = ""
        if after is not None:
            offset_str = ""
            if after.utcoffset() is None:
                offset_str = "+00:00"
            filter_str += f'createTime > "{after.isoformat("T") + offset_str}" AND '
        if before is not None:
            offset_str = ""
            if before.utcoffset() is None:
                offset_str = "+00:00"
            filter_str += f'createTime < "{before.isoformat("T") + offset_str}" AND '
        filter_str = filter_str[:-4]
        order_by = f"createTime {'ASC' if order_asc else 'DESC'}"

        # Get all messages from space
        while num_messages == -1 or len(all_msgs) < num_messages:
            req_msg = num_messages - len(all_msgs)

            result = (
                service.spaces()
                .messages()
                .list(
                    parent=parent,
                    pageSize=req_msg if num_messages != -1 else 1000,
                    pageToken=page_token,
                    filter=filter_str,
                    orderBy=order_by,
                    showDeleted=False,
                )
                .execute()
            )

            if result and "messages" in result:
                all_msgs.extend(result["messages"])

            # if no more messages to load
            if not result or "nextPageToken" not in result:
                break

            page_token = result["nextPageToken"]

        return all_msgs

    def _get_credentials(self) -> Any:
        """
        Get valid user credentials from storage.

        The file token.json stores the user's access and refresh tokens, and is
        created automatically when the authorization flow completes for the first
        time.

        Returns:
            Credentials, the obtained credential.

        """
        import os

        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request

        from google.oauth2.credentials import Credentials

        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        return creds

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Gets name identifier of class.
Source code in `llama-index-integrations/readers/llama-index-readers-google/llama_index/readers/google/chat/base.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Gets name identifier of class."""
    return "GoogleChatReader"

```
  
---|---  
###  load_data #
```
load_data(space_names: List[str], num_messages: int = -1, after: datetime = None, before: datetime = None, order_asc: bool = True) -> List[Document]

```

Loads documents from Google Chat.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`space_name` |  `List[str]` |  List of Space ID names found at top of URL (without the "space/"). |  _required_  
`num_messages` |  `int` |  Number of messages to load (may exceed this number). If -1, then loads all messages. Defaults to -1. |  `-1`  
`after` |  `datetime` |  Only search for messages after this datetime (UTC). Defaults to None. |  `None`  
`before` |  `datetime` |  Only search for messages before this datetime (UTC). Defaults to None. |  `None`  
`order_asc` |  `bool` |  If messages should be ordered by ascending time order. Defaults to True. |  `True`  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: List of document objects  
Source code in `llama-index-integrations/readers/llama-index-readers-google/llama_index/readers/google/chat/base.py`

| ```
def load_data(
    self,
    space_names: List[str],
    num_messages: int = -1,
    after: datetime = None,
    before: datetime = None,
    order_asc: bool = True,
) -> List[Document]:
    """
    Loads documents from Google Chat.

    Args:
        space_name (List[str]): List of Space ID names found at top of URL (without the "space/").
        num_messages (int, optional): Number of messages to load (may exceed this number). If -1, then loads all messages. Defaults to -1.
        after (datetime, optional): Only search for messages after this datetime (UTC). Defaults to None.
        before (datetime, optional): Only search for messages before this datetime (UTC). Defaults to None.
        order_asc (bool, optional): If messages should be ordered by ascending time order. Defaults to True.

    Returns:
        List[Document]: List of document objects

    """
    from googleapiclient.discovery import build

    # get credentials and create chat service
    credentials = self._get_credentials()
    service = build("chat", "v1", credentials=credentials)

    logger.info("Credentials successfully obtained.")

    res = []
    for space_name in space_names:
        all_msgs = self._get_msgs(
            service, space_name, num_messages, after, before, order_asc
        )  # gets raw API output in list of dict
        msgs_sorted = self._sort_msgs(
            space_name, all_msgs
        )  # puts messages into list of Document objects
        res.extend(msgs_sorted)
        logger.info(f"Successfully retrieved messages from {space_name}")

    return res

```
  
---|---  
##  GoogleDocsReader #
Bases: `BasePydanticReader`
Google Docs reader.
Reads a page from Google Docs
Source code in `llama-index-integrations/readers/llama-index-readers-google/llama_index/readers/google/docs/base.py`

| ```
class GoogleDocsReader(BasePydanticReader):
    """
    Google Docs reader.

    Reads a page from Google Docs

    """

    is_remote: bool = True

    split_on_heading_level: Optional[int] = Field(
        default=None,
        description="If set the document will be split on the specified heading level.",
    )

    include_toc: bool = Field(
        default=True, description="Include table of contents elements."
    )

    @classmethod
    def class_name(cls) -> str:
        return "GoogleDocsReader"

    def load_data(self, document_ids: List[str]) -> List[Document]:
        """
        Load data from the input directory.

        Args:
            document_ids (List[str]): a list of document ids.

        """
        if document_ids is None:
            raise ValueError('Must specify a "document_ids" in `load_kwargs`.')

        results = []
        for document_id in document_ids:
            docs = self._load_doc(document_id)
            results.extend(docs)

        return results

    def _load_doc(self, document_id: str) -> str:
        """
        Load a document from Google Docs.

        Args:
            document_id: the document id.

        Returns:
            The document text.

        """
        credentials = self._get_credentials()
        docs_service = discovery.build("docs", "v1", credentials=credentials)
        google_doc = docs_service.documents().get(documentId=document_id).execute()
        google_doc_content = google_doc.get("body").get("content")

        doc_metadata = {"document_id": document_id}

        return self._structural_elements_to_docs(google_doc_content, doc_metadata)

    def _get_credentials(self) -> Any:
        """
        Get valid user credentials from storage.

        The file token.json stores the user's access and refresh tokens, and is
        created automatically when the authorization flow completes for the first
        time.

        Returns:
            Credentials, the obtained credential.

        """
        creds = None
        port = 8080
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )

                with open("credentials.json") as json_file:
                    client_config = json.load(json_file)
                    redirect_uris = client_config["web"].get("redirect_uris", [])
                    if len(redirect_uris) > 0:
                        port = int(redirect_uris[0].strip("/").split(":")[-1])

                creds = flow.run_local_server(port=port)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        return creds

    def _read_paragraph_element(self, element: Any) -> Any:
        """
        Return the text in the given ParagraphElement.

        Args:
            element: a ParagraphElement from a Google Doc.

        """
        text_run = element.get("textRun")
        if not text_run:
            return ""
        return text_run.get("content")

    def _read_structural_elements(self, elements: List[Any]) -> Any:
        """
        Recurse through a list of Structural Elements.

        Read a document's text where text may be in nested elements.

        Args:
            elements: a list of Structural Elements.

        """
        text = ""
        for value in elements:
            if "paragraph" in value:
                elements = value.get("paragraph").get("elements")
                for elem in elements:
                    text += self._read_paragraph_element(elem)
            elif "table" in value:
                # The text in table cells are in nested Structural Elements
                # and tables may be nested.
                table = value.get("table")
                for row in table.get("tableRows"):
                    cells = row.get("tableCells")
                    for cell in cells:
                        text += self._read_structural_elements(cell.get("content"))
            elif "tableOfContents" in value:
                # The text in the TOC is also in a Structural Element.
                toc = value.get("tableOfContents")
                text += self._read_structural_elements(toc.get("content"))
        return text

    def _determine_heading_level(self, element):
        """
        Extracts the heading level, label, and ID from a document element.

        Args:
            element: a Structural Element.

        """
        level = None
        heading_key = None
        heading_id = None
        if self.split_on_heading_level and "paragraph" in element:
            style = element.get("paragraph").get("paragraphStyle")
            style_type = style.get("namedStyleType", "")
            heading_id = style.get("headingId", None)
            if style_type == "TITLE":
                level = 0
                heading_key = "title"
            elif style_type.startswith("HEADING_"):
                level = int(style_type.split("_")[1])
                if level > self.split_on_heading_level:
                    return None, None, None

                heading_key = f"Header {level}"

        return level, heading_key, heading_id

    def _generate_doc_id(self, metadata: dict):
        if "heading_id" in metadata:
            heading_id = metadata["heading_id"]
        else:
            heading_id = "".join(
                random.choices(string.ascii_letters + string.digits, k=8)
            )
        return f"{metadata['document_id']}_{heading_id}"

    def _structural_elements_to_docs(
        self, elements: List[Any], doc_metadata: dict
    ) -> Any:
        """
        Recurse through a list of Structural Elements.

        Split documents on heading if split_on_heading_level is set.

        Args:
            elements: a list of Structural Elements.

        """
        docs = []

        current_heading_level = self.split_on_heading_level

        metadata = doc_metadata.copy()
        text = ""
        for value in elements:
            element_text = self._read_structural_elements([value])

            level, heading_key, heading_id = self._determine_heading_level(value)

            if level is not None:
                if level == self.split_on_heading_level:
                    if text.strip():
                        docs.append(
                            Document(
                                id_=self._generate_doc_id(metadata),
                                text=text,
                                metadata=metadata.copy(),
                            )
                        )
                        text = ""
                    if "heading_id" in metadata:
                        metadata["heading_id"] = heading_id
                elif level < current_heading_level:
                    metadata = doc_metadata.copy()

                metadata[heading_key] = element_text
                current_heading_level = level
            else:
                text += element_text

        if text:
            if docs:
                id_ = self._generate_doc_id(metadata)
            else:
                id_ = metadata["document_id"]
            docs.append(Document(id_=id_, text=text, metadata=metadata))

        return docs

```
  
---|---  
###  load_data #
```
load_data(document_ids: List[str]) -> List[Document]

```

Load data from the input directory.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`document_ids` |  `List[str]` |  a list of document ids. |  _required_  
Source code in `llama-index-integrations/readers/llama-index-readers-google/llama_index/readers/google/docs/base.py`

| ```
def load_data(self, document_ids: List[str]) -> List[Document]:
    """
    Load data from the input directory.

    Args:
        document_ids (List[str]): a list of document ids.

    """
    if document_ids is None:
        raise ValueError('Must specify a "document_ids" in `load_kwargs`.')

    results = []
    for document_id in document_ids:
        docs = self._load_doc(document_id)
        results.extend(docs)

    return results

```
  
---|---  
##  GoogleDriveReader #
Bases: `BasePydanticReader`, `ResourcesReaderMixin`, `FileSystemReaderMixin`
Google Drive Reader.
Reads files from Google Drive. Credentials passed directly to the constructor will take precedence over those passed as file paths.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`drive_id` |  `Optional[str]` |  Drive id of the shared drive in google drive. |  `None`  
`folder_id` |  `Optional[str]` |  Folder id of the folder in google drive. |  `None`  
`file_ids` |  `Optional[str]` |  File ids of the files in google drive. |  `None`  
`query_string` |  `Optional[str]` |  A more generic query string to filter the documents, e.g. "name contains 'test'". It gives more flexibility to filter the documents. More info: https://developers.google.com/drive/api/v3/search-files |  `None`  
`is_cloud` |  `Optional[bool]` |  Whether the reader is being used in a cloud environment. Will not save credentials to disk if so. Defaults to False. |  `False`  
`credentials_path` |  `Optional[str]` |  Path to client config file. Defaults to None. |  `'credentials.json'`  
`token_path` |  `Optional[str]` |  Path to authorized user info file. Defaults to None. |  `'token.json'`  
`service_account_key_path` |  `Optional[str]` |  Path to service account key file. Defaults to None. |  `'service_account_key.json'`  
`client_config` |  `Optional[dict]` |  Dictionary containing client config. Defaults to None. |  `None`  
`authorized_user_info` |  `Optional[dict]` |  Dicstionary containing authorized user info. Defaults to None. |  `None`  
`service_account_key` |  `Optional[dict]` |  Dictionary containing service account key. Defaults to None. |  `None`  
`file_extractor` |  `Optional[Dict[str, BaseReader]]` |  A mapping of file extension to a BaseReader class that specifies how to convert that file to text. See `SimpleDirectoryReader` for more details. |  `None`  
Source code in `llama-index-integrations/readers/llama-index-readers-google/llama_index/readers/google/drive/base.py`

| ```
class GoogleDriveReader(
    BasePydanticReader, ResourcesReaderMixin, FileSystemReaderMixin
):
    """
    Google Drive Reader.

    Reads files from Google Drive. Credentials passed directly to the constructor
    will take precedence over those passed as file paths.

    Args:
        drive_id (Optional[str]): Drive id of the shared drive in google drive.
        folder_id (Optional[str]): Folder id of the folder in google drive.
        file_ids (Optional[str]): File ids of the files in google drive.
        query_string: A more generic query string to filter the documents, e.g. "name contains 'test'".
            It gives more flexibility to filter the documents. More info: https://developers.google.com/drive/api/v3/search-files
        is_cloud (Optional[bool]): Whether the reader is being used in
            a cloud environment. Will not save credentials to disk if so.
            Defaults to False.
        credentials_path (Optional[str]): Path to client config file.
            Defaults to None.
        token_path (Optional[str]): Path to authorized user info file. Defaults
            to None.
        service_account_key_path (Optional[str]): Path to service account key
            file. Defaults to None.
        client_config (Optional[dict]): Dictionary containing client config.
            Defaults to None.
        authorized_user_info (Optional[dict]): Dicstionary containing authorized
            user info. Defaults to None.
        service_account_key (Optional[dict]): Dictionary containing service
            account key. Defaults to None.
        file_extractor (Optional[Dict[str, BaseReader]]): A mapping of file
            extension to a BaseReader class that specifies how to convert that
            file to text. See `SimpleDirectoryReader` for more details.

    """

    drive_id: Optional[str] = None
    folder_id: Optional[str] = None
    file_ids: Optional[List[str]] = None
    query_string: Optional[str] = None
    client_config: Optional[dict] = None
    authorized_user_info: Optional[dict] = None
    service_account_key: Optional[dict] = None
    token_path: Optional[str] = None
    file_extractor: Optional[Dict[str, Union[str, BaseReader]]] = Field(
        default=None, exclude=True
    )

    _is_cloud: bool = PrivateAttr(default=False)
    _creds: Credentials = PrivateAttr()
    _mimetypes: dict = PrivateAttr()

    def __init__(
        self,
        drive_id: Optional[str] = None,
        folder_id: Optional[str] = None,
        file_ids: Optional[List[str]] = None,
        query_string: Optional[str] = None,
        is_cloud: Optional[bool] = False,
        credentials_path: str = "credentials.json",
        token_path: str = "token.json",
        service_account_key_path: str = "service_account_key.json",
        client_config: Optional[dict] = None,
        authorized_user_info: Optional[dict] = None,
        service_account_key: Optional[dict] = None,
        file_extractor: Optional[Dict[str, Union[str, BaseReader]]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize with parameters."""
        # Read the file contents so they can be serialized and stored.
        if client_config is None and os.path.isfile(credentials_path):
            with open(credentials_path, encoding="utf-8") as json_file:
                client_config = json.load(json_file)

        if authorized_user_info is None and os.path.isfile(token_path):
            with open(token_path, encoding="utf-8") as json_file:
                authorized_user_info = json.load(json_file)

        if service_account_key is None and os.path.isfile(service_account_key_path):
            with open(service_account_key_path, encoding="utf-8") as json_file:
                service_account_key = json.load(json_file)

        if (
            client_config is None
            and service_account_key is None
            and authorized_user_info is None
        ):
            raise ValueError(
                "Must specify `client_config` or `service_account_key` or `authorized_user_info`."
            )

        super().__init__(
            drive_id=drive_id,
            folder_id=folder_id,
            file_ids=file_ids,
            query_string=query_string,
            client_config=client_config,
            authorized_user_info=authorized_user_info,
            service_account_key=service_account_key,
            token_path=token_path,
            file_extractor=file_extractor,
            **kwargs,
        )

        self._creds = None
        self._is_cloud = is_cloud
        # Download Google Docs/Slides/Sheets as actual files
        # See https://developers.google.com/drive/v3/web/mime-types
        self._mimetypes = {
            "application/vnd.google-apps.document": {
                "mimetype": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "extension": ".docx",
            },
            "application/vnd.google-apps.spreadsheet": {
                "mimetype": (
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ),
                "extension": ".xlsx",
            },
            "application/vnd.google-apps.presentation": {
                "mimetype": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "extension": ".pptx",
            },
        }

    @classmethod
    def class_name(cls) -> str:
        return "GoogleDriveReader"

    def _get_credentials(self) -> Tuple[Credentials]:
        """
        Authenticate with Google and save credentials.
        Download the service_account_key.json file with these instructions: https://cloud.google.com/iam/docs/keys-create-delete.

        IMPORTANT: Make sure to share the folders / files with the service account. Otherwise it will fail to read the docs

        Returns:
            credentials

        """
        # First, we need the Google API credentials for the app
        creds = None

        if self.authorized_user_info is not None:
            creds = Credentials.from_authorized_user_info(
                self.authorized_user_info, SCOPES
            )
        elif self.service_account_key is not None:
            return service_account.Credentials.from_service_account_info(
                self.service_account_key, scopes=SCOPES
            )

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_config(self.client_config, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            if not self._is_cloud:
                with open(self.token_path, "w", encoding="utf-8") as token:
                    token.write(creds.to_json())

        return creds

    def _get_drive_link(self, file_id: str) -> str:
        return f"https://drive.google.com/file/d/{file_id}/view"

    def _get_relative_path(
        self, service, file_id: str, root_folder_id: Optional[str] = None
    ) -> str:
        """Get the relative path from root_folder_id to file_id."""
        try:
            # Get file details including parents
            file = (
                service.files()
                .get(fileId=file_id, supportsAllDrives=True, fields="name, parents")
                .execute()
            )

            path_parts = [file["name"]]

            if not root_folder_id:
                return file["name"]

            # Traverse up through parents until we reach root_folder_id or can't access anymore
            try:
                current_parent = file.get("parents", [None])[0]
                while current_parent:
                    # If we reach the root folder, stop
                    if current_parent == root_folder_id:
                        break

                    try:
                        parent = (
                            service.files()
                            .get(
                                fileId=current_parent,
                                supportsAllDrives=True,
                                fields="name, parents",
                            )
                            .execute()
                        )
                        path_parts.insert(0, parent["name"])
                        current_parent = parent.get("parents", [None])[0]
                    except Exception as e:
                        logger.debug(f"Stopped at parent {current_parent}: {e!s}")
                        break

            except Exception as e:
                logger.debug(f"Could not access parents for {file_id}: {e!s}")

            return "/".join(path_parts)

        except Exception as e:
            logger.warning(f"Could not get path for file {file_id}: {e}")
            return file["name"]

    def _get_fileids_meta(
        self,
        drive_id: Optional[str] = None,
        folder_id: Optional[str] = None,
        file_id: Optional[str] = None,
        mime_types: Optional[List[str]] = None,
        query_string: Optional[str] = None,
        current_path: Optional[str] = None,
    ) -> List[List[str]]:
        """
        Get file ids present in folder/ file id
        Args:
            drive_id: Drive id of the shared drive in google drive.
            folder_id: folder id of the folder in google drive.
            file_id: file id of the file in google drive
            mime_types: The mimeTypes you want to allow e.g.: "application/vnd.google-apps.document"
            query_string: A more generic query string to filter the documents, e.g. "name contains 'test'".

        Returns:
            metadata: List of metadata of filde ids.

        """
        from googleapiclient.discovery import build

        fileids_meta = []
        try:
            service = build("drive", "v3", credentials=self._creds)

            if folder_id and not file_id:
                try:
                    folder = (
                        service.files()
                        .get(fileId=folder_id, supportsAllDrives=True, fields="name")
                        .execute()
                    )
                    current_path = (
                        f"{current_path}/{folder['name']}"
                        if current_path
                        else folder["name"]
                    )
                except Exception as e:
                    logger.warning(f"Could not get folder name: {e}")

                folder_mime_type = "application/vnd.google-apps.folder"
                query = "('" + folder_id + "' in parents)"

                # Add mimeType filter to query
                if mime_types:
                    if folder_mime_type not in mime_types:
                        mime_types.append(folder_mime_type)  # keep the recursiveness
                    mime_query = " or ".join(
                        [f"mimeType='{mime_type}'" for mime_type in mime_types]
                    )
                    query += f" and ({mime_query})"

                # Add query string filter
                if query_string:
                    # to keep the recursiveness, we need to add folder_mime_type to the mime_types
                    query += (
                        f" and ((mimeType='{folder_mime_type}') or ({query_string}))"
                    )

                items = []
                page_token = ""
                # get files taking into account that the results are paginated
                while True:
                    if drive_id:
                        results = (
                            service.files()
                            .list(
                                q=query,
                                driveId=drive_id,
                                corpora="drive",
                                includeItemsFromAllDrives=True,
                                supportsAllDrives=True,
                                fields="*",
                                pageToken=page_token,
                            )
                            .execute()
                        )
                    else:
                        results = (
                            service.files()
                            .list(
                                q=query,
                                includeItemsFromAllDrives=True,
                                supportsAllDrives=True,
                                fields="*",
                                pageToken=page_token,
                            )
                            .execute()
                        )
                    items.extend(results.get("files", []))
                    page_token = results.get("nextPageToken", None)
                    if page_token is None:
                        break

                for item in items:
                    item_path = (
                        f"{current_path}/{item['name']}"
                        if current_path
                        else item["name"]
                    )

                    if item["mimeType"] == folder_mime_type:
                        if drive_id:
                            fileids_meta.extend(
                                self._get_fileids_meta(
                                    drive_id=drive_id,
                                    folder_id=item["id"],
                                    mime_types=mime_types,
                                    query_string=query_string,
                                    current_path=current_path,
                                )
                            )
                        else:
                            fileids_meta.extend(
                                self._get_fileids_meta(
                                    folder_id=item["id"],
                                    mime_types=mime_types,
                                    query_string=query_string,
                                    current_path=current_path,
                                )
                            )
                    else:
                        # Check if file doesn't belong to a Shared Drive. "owners" doesn't exist in a Shared Drive
                        is_shared_drive = "driveId" in item
                        author = (
                            item["owners"][0]["displayName"]
                            if not is_shared_drive
                            else "Shared Drive"
                        )
                        fileids_meta.append(
                            (
                                item["id"],
                                author,
                                item_path,
                                item["mimeType"],
                                item["createdTime"],
                                item["modifiedTime"],
                                self._get_drive_link(item["id"]),
                            )
                        )
            else:
                # Get the file details
                file = (
                    service.files()
                    .get(fileId=file_id, supportsAllDrives=True, fields="*")
                    .execute()
                )
                # Get metadata of the file
                is_shared_drive = "driveId" in file
                author = (
                    file["owners"][0]["displayName"]
                    if not is_shared_drive
                    else "Shared Drive"
                )

                # Get the full file path
                file_path = self._get_relative_path(
                    service, file_id, folder_id or self.folder_id
                )

                fileids_meta.append(
                    (
                        file["id"],
                        author,
                        file_path,
                        file["mimeType"],
                        file["createdTime"],
                        file["modifiedTime"],
                        self._get_drive_link(file["id"]),
                    )
                )
            return fileids_meta

        except Exception as e:
            logger.error(
                f"An error occurred while getting fileids metadata: {e}", exc_info=True
            )
            return fileids_meta

    def _download_file(self, fileid: str, filename: str) -> str:
        """
        Download the file with fileid and filename
        Args:
            fileid: file id of the file in google drive
            filename: filename with which it will be downloaded
        Returns:
            The downloaded filename, which may have a new extension.
        """
        from io import BytesIO

        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseDownload

        try:
            # Get file details
            service = build("drive", "v3", credentials=self._creds)
            file = service.files().get(fileId=fileid, supportsAllDrives=True).execute()

            if file["mimeType"] in self._mimetypes:
                download_mimetype = self._mimetypes[file["mimeType"]]["mimetype"]
                download_extension = self._mimetypes[file["mimeType"]]["extension"]
                new_file_name = filename + download_extension

                # Download and convert file
                request = service.files().export_media(
                    fileId=fileid, mimeType=download_mimetype
                )
            else:
                # we should have a file extension to allow the readers to work
                _, download_extension = os.path.splitext(file.get("name", ""))
                new_file_name = filename + download_extension

                # Download file without conversion
                request = service.files().get_media(fileId=fileid)

            # Download file data
            file_data = BytesIO()
            downloader = MediaIoBaseDownload(file_data, request)
            done = False

            while not done:
                status, done = downloader.next_chunk()

            # Save the downloaded file
            with open(new_file_name, "wb") as f:
                f.write(file_data.getvalue())

            return new_file_name
        except Exception as e:
            logger.error(
                f"An error occurred while downloading file: {e}", exc_info=True
            )

    def _load_data_fileids_meta(self, fileids_meta: List[List[str]]) -> List[Document]:
        """
        Load data from fileids metadata
        Args:
            fileids_meta: metadata of fileids in google drive.

        Returns:
            Lis[Document]: List of Document of data present in fileids.

        """
        try:
            with tempfile.TemporaryDirectory() as temp_dir:

                def get_metadata(filename):
                    return metadata[filename]

                temp_dir = Path(temp_dir)
                metadata = {}

                for fileid_meta in fileids_meta:
                    # Download files and name them with their fileid
                    fileid = fileid_meta[0]
                    filepath = os.path.join(temp_dir, fileid)
                    final_filepath = self._download_file(fileid, filepath)

                    # Add metadata of the file to metadata dictionary
                    metadata[final_filepath] = {
                        "file id": fileid_meta[0],
                        "author": fileid_meta[1],
                        "file path": fileid_meta[2],
                        "mime type": fileid_meta[3],
                        "created at": fileid_meta[4],
                        "modified at": fileid_meta[5],
                    }
                loader = SimpleDirectoryReader(
                    temp_dir,
                    file_extractor=self.file_extractor,
                    file_metadata=get_metadata,
                )
                documents = loader.load_data()
                for doc in documents:
                    doc.id_ = doc.metadata.get("file id", doc.id_)

            return documents
        except Exception as e:
            logger.error(
                f"An error occurred while loading data from fileids meta: {e}",
                exc_info=True,
            )

    def _load_from_file_ids(
        self,
        drive_id: Optional[str],
        file_ids: List[str],
        mime_types: Optional[List[str]],
        query_string: Optional[str],
    ) -> List[Document]:
        """
        Load data from file ids
        Args:
            file_ids: File ids of the files in google drive.
            mime_types: The mimeTypes you want to allow e.g.: "application/vnd.google-apps.document"
            query_string: List of query strings to filter the documents, e.g. "name contains 'test'".

        Returns:
            Document: List of Documents of text.

        """
        try:
            fileids_meta = []
            for file_id in file_ids:
                fileids_meta.extend(
                    self._get_fileids_meta(
                        drive_id=drive_id,
                        file_id=file_id,
                        mime_types=mime_types,
                        query_string=query_string,
                    )
                )
            return self._load_data_fileids_meta(fileids_meta)
        except Exception as e:
            logger.error(
                f"An error occurred while loading with fileid: {e}", exc_info=True
            )

    def _load_from_folder(
        self,
        drive_id: Optional[str],
        folder_id: str,
        mime_types: Optional[List[str]],
        query_string: Optional[str],
    ) -> List[Document]:
        """
        Load data from folder_id.

        Args:
            drive_id: Drive id of the shared drive in google drive.
            folder_id: folder id of the folder in google drive.
            mime_types: The mimeTypes you want to allow e.g.: "application/vnd.google-apps.document"
            query_string: A more generic query string to filter the documents, e.g. "name contains 'test'".

        Returns:
            Document: List of Documents of text.

        """
        try:
            fileids_meta = self._get_fileids_meta(
                drive_id=drive_id,
                folder_id=folder_id,
                mime_types=mime_types,
                query_string=query_string,
            )
            return self._load_data_fileids_meta(fileids_meta)
        except Exception as e:
            logger.error(
                f"An error occurred while loading from folder: {e}", exc_info=True
            )

    def load_data(
        self,
        drive_id: Optional[str] = None,
        folder_id: Optional[str] = None,
        file_ids: Optional[List[str]] = None,
        mime_types: Optional[List[str]] = None,  # Deprecated
        query_string: Optional[str] = None,
    ) -> List[Document]:
        """
        Load data from the folder id or file ids.

        Args:
            drive_id: Drive id of the shared drive in google drive.
            folder_id: Folder id of the folder in google drive.
            file_ids: File ids of the files in google drive.
            mime_types: The mimeTypes you want to allow e.g.: "application/vnd.google-apps.document"
            query_string: A more generic query string to filter the documents, e.g. "name contains 'test'".
                It gives more flexibility to filter the documents. More info: https://developers.google.com/drive/api/v3/search-files

        Returns:
            List[Document]: A list of documents.

        """
        self._creds = self._get_credentials()

        # If no arguments are provided to load_data, default to the object attributes
        if drive_id is None:
            drive_id = self.drive_id
        if folder_id is None:
            folder_id = self.folder_id
        if file_ids is None:
            file_ids = self.file_ids
        if query_string is None:
            query_string = self.query_string

        if folder_id:
            return self._load_from_folder(drive_id, folder_id, mime_types, query_string)
        elif file_ids:
            return self._load_from_file_ids(
                drive_id, file_ids, mime_types, query_string
            )
        else:
            logger.warning("Either 'folder_id' or 'file_ids' must be provided.")
            return []

    def list_resources(self, **kwargs) -> List[str]:
        """List resources in the specified Google Drive folder or files."""
        self._creds = self._get_credentials()

        drive_id = kwargs.get("drive_id", self.drive_id)
        folder_id = kwargs.get("folder_id", self.folder_id)
        file_ids = kwargs.get("file_ids", self.file_ids)
        query_string = kwargs.get("query_string", self.query_string)

        if folder_id:
            fileids_meta = self._get_fileids_meta(
                drive_id, folder_id, query_string=query_string
            )
        elif file_ids:
            fileids_meta = []
            for file_id in file_ids:
                fileids_meta.extend(
                    self._get_fileids_meta(
                        drive_id, file_id=file_id, query_string=query_string
                    )
                )
        else:
            raise ValueError("Either 'folder_id' or 'file_ids' must be provided.")

        return [meta[0] for meta in fileids_meta]  # Return list of file IDs

    def get_resource_info(self, resource_id: str, **kwargs) -> Dict:
        """Get information about a specific Google Drive resource."""
        self._creds = self._get_credentials()

        fileids_meta = self._get_fileids_meta(file_id=resource_id)
        if not fileids_meta:
            raise ValueError(f"Resource with ID {resource_id} not found.")

        meta = fileids_meta[0]
        return {
            "file_path": meta[2],
            "file_size": None,
            "last_modified_date": meta[5],
            "content_hash": None,
            "content_type": meta[3],
            "author": meta[1],
            "created_date": meta[4],
            "drive_link": meta[6],
        }

    def load_resource(self, resource_id: str, **kwargs) -> List[Document]:
        """Load a specific resource from Google Drive."""
        return self._load_from_file_ids(
            self.drive_id, [resource_id], None, self.query_string
        )

    def read_file_content(self, file_path: Union[str, Path], **kwargs) -> bytes:
        """Read the content of a specific file from Google Drive."""
        self._creds = self._get_credentials()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "temp_file")
            downloaded_file = self._download_file(file_path, temp_file)
            with open(downloaded_file, "rb") as file:
                return file.read()

```
  
---|---  
###  load_data #
```
load_data(drive_id: Optional[str] = None, folder_id: Optional[str] = None, file_ids: Optional[List[str]] = None, mime_types: Optional[List[str]] = None, query_string: Optional[str] = None) -> List[Document]

```

Load data from the folder id or file ids.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`drive_id` |  `Optional[str]` |  Drive id of the shared drive in google drive. |  `None`  
`folder_id` |  `Optional[str]` |  Folder id of the folder in google drive. |  `None`  
`file_ids` |  `Optional[List[str]]` |  File ids of the files in google drive. |  `None`  
`mime_types` |  `Optional[List[str]]` |  The mimeTypes you want to allow e.g.: "application/vnd.google-apps.document" |  `None`  
`query_string` |  `Optional[str]` |  A more generic query string to filter the documents, e.g. "name contains 'test'". It gives more flexibility to filter the documents. More info: https://developers.google.com/drive/api/v3/search-files |  `None`  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: A list of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-google/llama_index/readers/google/drive/base.py`

| ```
def load_data(
    self,
    drive_id: Optional[str] = None,
    folder_id: Optional[str] = None,
    file_ids: Optional[List[str]] = None,
    mime_types: Optional[List[str]] = None,  # Deprecated
    query_string: Optional[str] = None,
) -> List[Document]:
    """
    Load data from the folder id or file ids.

    Args:
        drive_id: Drive id of the shared drive in google drive.
        folder_id: Folder id of the folder in google drive.
        file_ids: File ids of the files in google drive.
        mime_types: The mimeTypes you want to allow e.g.: "application/vnd.google-apps.document"
        query_string: A more generic query string to filter the documents, e.g. "name contains 'test'".
            It gives more flexibility to filter the documents. More info: https://developers.google.com/drive/api/v3/search-files

    Returns:
        List[Document]: A list of documents.

    """
    self._creds = self._get_credentials()

    # If no arguments are provided to load_data, default to the object attributes
    if drive_id is None:
        drive_id = self.drive_id
    if folder_id is None:
        folder_id = self.folder_id
    if file_ids is None:
        file_ids = self.file_ids
    if query_string is None:
        query_string = self.query_string

    if folder_id:
        return self._load_from_folder(drive_id, folder_id, mime_types, query_string)
    elif file_ids:
        return self._load_from_file_ids(
            drive_id, file_ids, mime_types, query_string
        )
    else:
        logger.warning("Either 'folder_id' or 'file_ids' must be provided.")
        return []

```
  
---|---  
###  list_resources #
```
list_resources(**kwargs) -> List[str]

```

List resources in the specified Google Drive folder or files.
Source code in `llama-index-integrations/readers/llama-index-readers-google/llama_index/readers/google/drive/base.py`

| ```
def list_resources(self, **kwargs) -> List[str]:
    """List resources in the specified Google Drive folder or files."""
    self._creds = self._get_credentials()

    drive_id = kwargs.get("drive_id", self.drive_id)
    folder_id = kwargs.get("folder_id", self.folder_id)
    file_ids = kwargs.get("file_ids", self.file_ids)
    query_string = kwargs.get("query_string", self.query_string)

    if folder_id:
        fileids_meta = self._get_fileids_meta(
            drive_id, folder_id, query_string=query_string
        )
    elif file_ids:
        fileids_meta = []
        for file_id in file_ids:
            fileids_meta.extend(
                self._get_fileids_meta(
                    drive_id, file_id=file_id, query_string=query_string
                )
            )
    else:
        raise ValueError("Either 'folder_id' or 'file_ids' must be provided.")

    return [meta[0] for meta in fileids_meta]  # Return list of file IDs

```
  
---|---  
###  get_resource_info #
```
get_resource_info(resource_id: str, **kwargs) -> Dict

```

Get information about a specific Google Drive resource.
Source code in `llama-index-integrations/readers/llama-index-readers-google/llama_index/readers/google/drive/base.py`

| ```
def get_resource_info(self, resource_id: str, **kwargs) -> Dict:
    """Get information about a specific Google Drive resource."""
    self._creds = self._get_credentials()

    fileids_meta = self._get_fileids_meta(file_id=resource_id)
    if not fileids_meta:
        raise ValueError(f"Resource with ID {resource_id} not found.")

    meta = fileids_meta[0]
    return {
        "file_path": meta[2],
        "file_size": None,
        "last_modified_date": meta[5],
        "content_hash": None,
        "content_type": meta[3],
        "author": meta[1],
        "created_date": meta[4],
        "drive_link": meta[6],
    }

```
  
---|---  
###  load_resource #
```
load_resource(resource_id: str, **kwargs) -> List[Document]

```

Load a specific resource from Google Drive.
Source code in `llama-index-integrations/readers/llama-index-readers-google/llama_index/readers/google/drive/base.py`

| ```
def load_resource(self, resource_id: str, **kwargs) -> List[Document]:
    """Load a specific resource from Google Drive."""
    return self._load_from_file_ids(
        self.drive_id, [resource_id], None, self.query_string
    )

```
  
---|---  
###  read_file_content #
```
read_file_content(file_path: Union[str, Path], **kwargs) -> bytes

```

Read the content of a specific file from Google Drive.
Source code in `llama-index-integrations/readers/llama-index-readers-google/llama_index/readers/google/drive/base.py`

| ```
def read_file_content(self, file_path: Union[str, Path], **kwargs) -> bytes:
    """Read the content of a specific file from Google Drive."""
    self._creds = self._get_credentials()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = os.path.join(temp_dir, "temp_file")
        downloaded_file = self._download_file(file_path, temp_file)
        with open(downloaded_file, "rb") as file:
            return file.read()

```
  
---|---  
##  GoogleKeepReader #
Bases: `BaseReader`
Google Keep reader.
Reads notes from Google Keep
Source code in `llama-index-integrations/readers/llama-index-readers-google/llama_index/readers/google/keep/base.py`

| ```
class GoogleKeepReader(BaseReader):
    """
    Google Keep reader.

    Reads notes from Google Keep

    """

    def load_data(self, document_ids: List[str]) -> List[Document]:
        """
        Load data from the document_ids.

        Args:
            document_ids (List[str]): a list of note ids.

        """
        keep = self._get_keep()

        if document_ids is None:
            raise ValueError('Must specify a "document_ids" in `load_kwargs`.')

        results = []
        for note_id in document_ids:
            note = keep.get(note_id)
            if note is None:
                raise ValueError(f"Note with id {note_id} not found.")
            text = f"Title: {note.title}\nContent: {note.text}"
            results.append(Document(text=text, extra_info={"note_id": note_id}))
        return results

    def load_all_notes(self) -> List[Document]:
        """Load all notes from Google Keep."""
        keep = self._get_keep()

        notes = keep.all()
        results = []
        for note in notes:
            text = f"Title: {note.title}\nContent: {note.text}"
            results.append(Document(text=text, extra_info={"note_id": note.id}))
        return results

    def _get_keep(self) -> Any:
        import gkeepapi

        """Get a Google Keep object with login."""
        # Read username and password from keep_credentials.json
        if os.path.exists("keep_credentials.json"):
            with open("keep_credentials.json") as f:
                credentials = json.load(f)
        else:
            raise RuntimeError("Failed to load keep_credentials.json.")

        keep = gkeepapi.Keep()

        success = keep.login(credentials["username"], credentials["password"])
        if not success:
            raise RuntimeError("Failed to login to Google Keep.")

        return keep

```
  
---|---  
###  load_data #
```
load_data(document_ids: List[str]) -> List[Document]

```

Load data from the document_ids.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`document_ids` |  `List[str]` |  a list of note ids. |  _required_  
Source code in `llama-index-integrations/readers/llama-index-readers-google/llama_index/readers/google/keep/base.py`

| ```
def load_data(self, document_ids: List[str]) -> List[Document]:
    """
    Load data from the document_ids.

    Args:
        document_ids (List[str]): a list of note ids.

    """
    keep = self._get_keep()

    if document_ids is None:
        raise ValueError('Must specify a "document_ids" in `load_kwargs`.')

    results = []
    for note_id in document_ids:
        note = keep.get(note_id)
        if note is None:
            raise ValueError(f"Note with id {note_id} not found.")
        text = f"Title: {note.title}\nContent: {note.text}"
        results.append(Document(text=text, extra_info={"note_id": note_id}))
    return results

```
  
---|---  
###  load_all_notes #
```
load_all_notes() -> List[Document]

```

Load all notes from Google Keep.
Source code in `llama-index-integrations/readers/llama-index-readers-google/llama_index/readers/google/keep/base.py`

| ```
def load_all_notes(self) -> List[Document]:
    """Load all notes from Google Keep."""
    keep = self._get_keep()

    notes = keep.all()
    results = []
    for note in notes:
        text = f"Title: {note.title}\nContent: {note.text}"
        results.append(Document(text=text, extra_info={"note_id": note.id}))
    return results

```
  
---|---  
##  GoogleMapsTextSearchReader #
Bases: `BaseReader`
Source code in `llama-index-integrations/readers/llama-index-readers-google/llama_index/readers/google/maps/base.py`

| ```
class GoogleMapsTextSearchReader(BaseReader):
    def __init__(
        self,
        api_key: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key must be provided or set in the environment variables as 'GOOGLE_MAPS_API_KEY'"
            )

    def load_data(
        self,
        text: str,
        number_of_results: Optional[int] = DEFAULT_NUMBER_OF_RESULTS,
    ) -> List[Document]:
        """
        Load data from Google Maps.

        Args:
            text (str): the text to search for.
            number_of_results (Optional[int]): the number of results to return. Defaults to 20.

        """
        response = self._search_text_request(text, MAX_RESULTS_PER_PAGE)
        documents = []
        while "nextPageToken" in response:
            next_page_token = response["nextPageToken"]
            places = response.get("places", [])
            if len(places) == 0:
                break
            for place in places:
                formatted_address = place["formattedAddress"]
                average_rating = place["rating"]
                display_name = place["displayName"]
                if isinstance(display_name, dict):
                    display_name = display_name["text"]
                number_of_ratings = place["userRatingCount"]
                reviews = []
                for review in place["reviews"]:
                    review_text = review["text"]["text"]
                    author_name = review["authorAttribution"]["displayName"]
                    relative_publish_time = review["relativePublishTimeDescription"]
                    rating = review["rating"]
                    reviews.append(
                        Review(
                            author_name=author_name,
                            rating=rating,
                            text=review_text,
                            relative_publish_time=relative_publish_time,
                        )
                    )

                place = Place(
                    reviews=reviews,
                    address=formatted_address,
                    average_rating=average_rating,
                    display_name=display_name,
                    number_of_ratings=number_of_ratings,
                )
                reviews_text = "\n".join(
                    [
                        f"Author: {review.author_name}, Rating: {review.rating}, Text: {review.text}, Relative Publish Time: {review.relative_publish_time}"
                        for review in reviews
                    ]
                )
                place_text = f"Place: {place.display_name}, Address: {place.address}, Average Rating: {place.average_rating}, Number of Ratings: {place.number_of_ratings}"
                document_text = f"{place_text}\n{reviews_text}"

                if len(documents) == number_of_results:
                    return documents

                documents.append(Document(text=document_text, extra_info=place.dict()))
            response = self._search_text_request(
                text, MAX_RESULTS_PER_PAGE, next_page_token
            )

        return documents

    def lazy_load_data(self, *args: Any, **load_kwargs: Any) -> Iterable[Document]:
        """Load data lazily from Google Maps."""
        yield from self.load_data(*args, **load_kwargs)

    def _search_text_request(
        self, text, number_of_results, next_page_token: Optional[str] = None
    ) -> dict:
        """
        Send a request to the Google Maps Places API to search for text.

        Args:
            text (str): the text to search for.
            number_of_results (int): the number of results to return.
            next_page_token (Optional[str]): the next page token to get the next page of results.

        """
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": FIELD_MASK,
        }
        payload = json.dumps(
            {
                "textQuery": text,
                "pageSize": number_of_results,
                "pageToken": next_page_token,
            }
        )
        response = requests.post(SEARCH_TEXT_BASE_URL, headers=headers, data=payload)
        response.raise_for_status()
        return response.json()

```
  
---|---  
###  load_data #
```
load_data(text: str, number_of_results: Optional[int] = DEFAULT_NUMBER_OF_RESULTS) -> List[Document]

```

Load data from Google Maps.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`text` |  `str` |  the text to search for. |  _required_  
`number_of_results` |  `Optional[int]` |  the number of results to return. Defaults to 20. |  `DEFAULT_NUMBER_OF_RESULTS`  
Source code in `llama-index-integrations/readers/llama-index-readers-google/llama_index/readers/google/maps/base.py`

| ```
def load_data(
    self,
    text: str,
    number_of_results: Optional[int] = DEFAULT_NUMBER_OF_RESULTS,
) -> List[Document]:
    """
    Load data from Google Maps.

    Args:
        text (str): the text to search for.
        number_of_results (Optional[int]): the number of results to return. Defaults to 20.

    """
    response = self._search_text_request(text, MAX_RESULTS_PER_PAGE)
    documents = []
    while "nextPageToken" in response:
        next_page_token = response["nextPageToken"]
        places = response.get("places", [])
        if len(places) == 0:
            break
        for place in places:
            formatted_address = place["formattedAddress"]
            average_rating = place["rating"]
            display_name = place["displayName"]
            if isinstance(display_name, dict):
                display_name = display_name["text"]
            number_of_ratings = place["userRatingCount"]
            reviews = []
            for review in place["reviews"]:
                review_text = review["text"]["text"]
                author_name = review["authorAttribution"]["displayName"]
                relative_publish_time = review["relativePublishTimeDescription"]
                rating = review["rating"]
                reviews.append(
                    Review(
                        author_name=author_name,
                        rating=rating,
                        text=review_text,
                        relative_publish_time=relative_publish_time,
                    )
                )

            place = Place(
                reviews=reviews,
                address=formatted_address,
                average_rating=average_rating,
                display_name=display_name,
                number_of_ratings=number_of_ratings,
            )
            reviews_text = "\n".join(
                [
                    f"Author: {review.author_name}, Rating: {review.rating}, Text: {review.text}, Relative Publish Time: {review.relative_publish_time}"
                    for review in reviews
                ]
            )
            place_text = f"Place: {place.display_name}, Address: {place.address}, Average Rating: {place.average_rating}, Number of Ratings: {place.number_of_ratings}"
            document_text = f"{place_text}\n{reviews_text}"

            if len(documents) == number_of_results:
                return documents

            documents.append(Document(text=document_text, extra_info=place.dict()))
        response = self._search_text_request(
            text, MAX_RESULTS_PER_PAGE, next_page_token
        )

    return documents

```
  
---|---  
###  lazy_load_data #
```
lazy_load_data(*args: Any, **load_kwargs: Any) -> Iterable[Document]

```

Load data lazily from Google Maps.
Source code in `llama-index-integrations/readers/llama-index-readers-google/llama_index/readers/google/maps/base.py`

| ```
def lazy_load_data(self, *args: Any, **load_kwargs: Any) -> Iterable[Document]:
    """Load data lazily from Google Maps."""
    yield from self.load_data(*args, **load_kwargs)

```
  
---|---  
##  GoogleSheetsReader #
Bases: `BasePydanticReader`
Google Sheets reader.
Reads a sheet as TSV from Google Sheets
Source code in `llama-index-integrations/readers/llama-index-readers-google/llama_index/readers/google/sheets/base.py`

| ```
class GoogleSheetsReader(BasePydanticReader):
    """
    Google Sheets reader.

    Reads a sheet as TSV from Google Sheets

    """

    is_remote: bool = True

    def __init__(self) -> None:
        """Initialize with parameters."""
        try:
            import google  # noqa
            import google_auth_oauthlib  # noqa
            import googleapiclient  # noqa
        except ImportError:
            raise ImportError(
                "`google_auth_oauthlib`, `googleapiclient` and `google` "
                "must be installed to use the GoogleSheetsReader.\n"
                "Please run `pip install --upgrade google-api-python-client "
                "google-auth-httplib2 google-auth-oauthlib`."
            )

    @classmethod
    def class_name(cls) -> str:
        return "GoogleSheetsReader"

    def load_data(self, spreadsheet_ids: List[str]) -> List[Document]:
        """
        Load data from the input directory.

        Args:
            spreadsheet_ids (List[str]): a list of document ids.

        """
        if spreadsheet_ids is None:
            raise ValueError('Must specify a "spreadsheet_ids" in `load_kwargs`.')

        results = []
        for spreadsheet_id in spreadsheet_ids:
            sheet = self._load_sheet(spreadsheet_id)
            results.append(
                Document(
                    id_=spreadsheet_id,
                    text=sheet,
                    metadata={"spreadsheet_id": spreadsheet_id},
                )
            )
        return results

    def load_data_in_pandas(self, spreadsheet_ids: List[str]) -> List[pd.DataFrame]:
        """
        Load data from the input directory.

        Args:
            spreadsheet_ids (List[str]): a list of document ids.

        """
        if spreadsheet_ids is None:
            raise ValueError('Must specify a "spreadsheet_ids" in `load_kwargs`.')

        results = []
        for spreadsheet_id in spreadsheet_ids:
            dataframes = self._load_sheet_in_pandas(spreadsheet_id)
            results.extend(dataframes)
        return results

    def _load_sheet(self, spreadsheet_id: str) -> str:
        """
        Load a sheet from Google Sheets.

        Args:
            spreadsheet_id: the sheet id.

        Returns:
            The sheet data.

        """
        credentials = self._get_credentials()
        sheets_service = discovery.build("sheets", "v4", credentials=credentials)
        spreadsheet_data = (
            sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        )
        sheets = spreadsheet_data.get("sheets")
        sheet_text = ""

        for sheet in sheets:
            properties = sheet.get("properties")
            title = properties.get("title")
            sheet_text += title + "\n"
            grid_props = properties.get("gridProperties")
            rows = grid_props.get("rowCount")
            cols = grid_props.get("columnCount")
            range_pattern = f"R1C1:R{rows}C{cols}"
            response = (
                sheets_service.spreadsheets()
                .values()
                .get(spreadsheetId=spreadsheet_id, range=range_pattern)
                .execute()
            )
            sheet_text += (
                "\n".join("\t".join(row) for row in response.get("values", [])) + "\n"
            )
        return sheet_text

    def _load_sheet_in_pandas(self, spreadsheet_id: str) -> List[pd.DataFrame]:
        """
        Load a sheet from Google Sheets.

        Args:
            spreadsheet_id: the sheet id.
            sheet_name: the sheet name.

        Returns:
            The sheet data.

        """
        credentials = self._get_credentials()
        sheets_service = discovery.build("sheets", "v4", credentials=credentials)
        sheet = sheets_service.spreadsheets()
        spreadsheet_data = sheet.get(spreadsheetId=spreadsheet_id).execute()
        sheets = spreadsheet_data.get("sheets")
        dataframes = []
        for sheet in sheets:
            properties = sheet.get("properties")
            title = properties.get("title")
            grid_props = properties.get("gridProperties")
            rows = grid_props.get("rowCount")
            cols = grid_props.get("columnCount")
            range_pattern = f"{title}!R1C1:R{rows}C{cols}"
            response = (
                sheets_service.spreadsheets()
                .values()
                .get(spreadsheetId=spreadsheet_id, range=range_pattern)
                .execute()
            )
            values = response.get("values", [])
            if not values:
                print(f"No data found in {title}")
            else:
                df = pd.DataFrame(values[1:], columns=values[0])
                dataframes.append(df)
        return dataframes

    def _get_credentials(self) -> Any:
        """
        Get valid user credentials from storage.

        The file token.json stores the user's access and refresh tokens, and is
        created automatically when the authorization flow completes for the first
        time.

        Returns:
            Credentials, the obtained credential.

        """
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        return creds

```
  
---|---  
###  load_data #
```
load_data(spreadsheet_ids: List[str]) -> List[Document]

```

Load data from the input directory.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`spreadsheet_ids` |  `List[str]` |  a list of document ids. |  _required_  
Source code in `llama-index-integrations/readers/llama-index-readers-google/llama_index/readers/google/sheets/base.py`

| ```
def load_data(self, spreadsheet_ids: List[str]) -> List[Document]:
    """
    Load data from the input directory.

    Args:
        spreadsheet_ids (List[str]): a list of document ids.

    """
    if spreadsheet_ids is None:
        raise ValueError('Must specify a "spreadsheet_ids" in `load_kwargs`.')

    results = []
    for spreadsheet_id in spreadsheet_ids:
        sheet = self._load_sheet(spreadsheet_id)
        results.append(
            Document(
                id_=spreadsheet_id,
                text=sheet,
                metadata={"spreadsheet_id": spreadsheet_id},
            )
        )
    return results

```
  
---|---  
###  load_data_in_pandas #
```
load_data_in_pandas(spreadsheet_ids: List[str]) -> List[DataFrame]

```

Load data from the input directory.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`spreadsheet_ids` |  `List[str]` |  a list of document ids. |  _required_  
Source code in `llama-index-integrations/readers/llama-index-readers-google/llama_index/readers/google/sheets/base.py`

| ```
def load_data_in_pandas(self, spreadsheet_ids: List[str]) -> List[pd.DataFrame]:
    """
    Load data from the input directory.

    Args:
        spreadsheet_ids (List[str]): a list of document ids.

    """
    if spreadsheet_ids is None:
        raise ValueError('Must specify a "spreadsheet_ids" in `load_kwargs`.')

    results = []
    for spreadsheet_id in spreadsheet_ids:
        dataframes = self._load_sheet_in_pandas(spreadsheet_id)
        results.extend(dataframes)
    return results

```
  
---|---
