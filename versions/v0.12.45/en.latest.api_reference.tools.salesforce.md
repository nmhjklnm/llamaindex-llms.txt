# Salesforce
##  SalesforceToolSpec #
Bases: `BaseToolSpec`
Salesforce tool spec.
Gives the agent the ability to interact with Salesforce using simple_salesforce
Source code in `llama-index-integrations/tools/llama-index-tools-salesforce/llama_index/tools/salesforce/base.py`

| ```
class SalesforceToolSpec(BaseToolSpec):
    """
    Salesforce tool spec.

    Gives the agent the ability to interact with Salesforce using simple_salesforce

    """

    spec_functions = ["execute_sosl", "execute_soql"]

    def __init__(self, **kargs) -> None:
        """Initialize with parameters for Salesforce connection."""
        from simple_salesforce import Salesforce

        self.sf = Salesforce(**kargs)

    def execute_sosl(self, search: str) -> str:
        """
        Returns the result of a Salesforce search as a dict decoded from
        the Salesforce response JSON payload.

        Arguments:
        * search -- the fully formatted SOSL search string, e.g.
                    `FIND {Waldo}`.

        """
        from simple_salesforce import SalesforceError

        try:
            res = self.sf.search(search)
        except SalesforceError as err:
            return f"Error running SOSL query: {err}"
        return res

    def execute_soql(self, query: str) -> str:
        """
        Returns the full set of results for the `query`. This is a
        convenience wrapper around `query(...)` and `query_more(...)`.
        The returned dict is the decoded JSON payload from the final call to
        Salesforce, but with the `totalSize` field representing the full
        number of results retrieved and the `records` list representing the
        full list of records retrieved.

        Arguments:
        * query -- the SOQL query to send to Salesforce, e.g.
                   SELECT Id FROM Lead WHERE Email = "waldo@somewhere.com".

        """
        from simple_salesforce import SalesforceError

        try:
            res = self.sf.query_all(query)
        except SalesforceError as err:
            return f"Error running SOQL query: {err}"
        return res

```
  
---|---  
###  execute_sosl #
```
execute_sosl(search: str) -> str

```

Returns the result of a Salesforce search as a dict decoded from the Salesforce response JSON payload.
  * search -- the fully formatted SOSL search string, e.g. `FIND {Waldo}`.

Source code in `llama-index-integrations/tools/llama-index-tools-salesforce/llama_index/tools/salesforce/base.py`

| ```
def execute_sosl(self, search: str) -> str:
    """
    Returns the result of a Salesforce search as a dict decoded from
    the Salesforce response JSON payload.

    Arguments:
    * search -- the fully formatted SOSL search string, e.g.
                `FIND {Waldo}`.

    """
    from simple_salesforce import SalesforceError

    try:
        res = self.sf.search(search)
    except SalesforceError as err:
        return f"Error running SOSL query: {err}"
    return res

```
  
---|---  
###  execute_soql #
```
execute_soql(query: str) -> str

```

Returns the full set of results for the `query`. This is a convenience wrapper around `query(...)` and `query_more(...)`. The returned dict is the decoded JSON payload from the final call to Salesforce, but with the `totalSize` field representing the full number of results retrieved and the `records` list representing the full list of records retrieved.
  * query -- the SOQL query to send to Salesforce, e.g. SELECT Id FROM Lead WHERE Email = "waldo@somewhere.com".

Source code in `llama-index-integrations/tools/llama-index-tools-salesforce/llama_index/tools/salesforce/base.py`

| ```
def execute_soql(self, query: str) -> str:
    """
    Returns the full set of results for the `query`. This is a
    convenience wrapper around `query(...)` and `query_more(...)`.
    The returned dict is the decoded JSON payload from the final call to
    Salesforce, but with the `totalSize` field representing the full
    number of results retrieved and the `records` list representing the
    full list of records retrieved.

    Arguments:
    * query -- the SOQL query to send to Salesforce, e.g.
               SELECT Id FROM Lead WHERE Email = "waldo@somewhere.com".

    """
    from simple_salesforce import SalesforceError

    try:
        res = self.sf.query_all(query)
    except SalesforceError as err:
        return f"Error running SOQL query: {err}"
    return res

```
  
---|---
