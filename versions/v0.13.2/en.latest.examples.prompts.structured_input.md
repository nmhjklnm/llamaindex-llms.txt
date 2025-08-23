# Structured Input for LLMs¶
It has been observed that most LLMs perfom better when prompted with XML-like content (you can see it in Anthropic's prompting guide, for instance).
We could refer to this kind of prompting as _structured input_ , and LlamaIndex offers you the possibility of chatting with LLMs exactly through this technique - let's go through an example in this notebook!
### 1. Install Needed Dependencies¶
> _Make sure to have`llama-index>=0.12.34` installed if you wish to follow this tutorial along without any problem😄_
In [ ]:
Copied!
```
! pip install -q llama-index

```

! pip install -q llama-index
```
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 7.6/7.6 MB 65.4 MB/s eta 0:00:00
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 284.6/284.6 kB 21.0 MB/s eta 0:00:00
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 41.0/41.0 kB 2.6 MB/s eta 0:00:00
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 40.4/40.4 kB 2.9 MB/s eta 0:00:00
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 309.7/309.7 kB 23.8 MB/s eta 0:00:00
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.2/1.2 MB 55.3 MB/s eta 0:00:00
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 50.9/50.9 kB 3.2 MB/s eta 0:00:00
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 129.3/129.3 kB 9.8 MB/s eta 0:00:00
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
ipython 7.34.0 requires jedi>=0.16, which is not installed.

```

In [ ]:
Copied!
```
! pip show llama-index | grep "Version"

```

! pip show llama-index | grep "Version"
```
Version: 0.12.50

```

### 2. Create a Prompt Template¶
In order to use the structured input, we need to create a prompt template that would have a Jinja expression (recognizable by the `{{}}`) with a specific filter (`to_xml`) that will turn inputs such as Pydantic `BaseModel` subclasses, dictionaries or JSON-like strings into XML representations.
In [ ]:
Copied!
```
from llama_index.core.prompts import RichPromptTemplate

template_str = "Please extract from the following XML code the contact details of the user:\n\n```xml\n{{ data | to_xml }}\n```\n\n"
prompt = RichPromptTemplate(template_str)

```

from llama_index.core.prompts import RichPromptTemplate template_str = "Please extract from the following XML code the contact details of the user:\n\n```xml\n{{ data | to_xml }}\n```\n\n" prompt = RichPromptTemplate(template_str)
Let's now try to format the input as a string, using different objects as `data`.
In [ ]:
Copied!
```
# Using a BaseModel

from pydantic import BaseModel
from typing import Dict
from IPython.display import Markdown, display


class User(BaseModel):
    name: str
    surname: str
    age: int
    email: str
    phone: str
    social_accounts: Dict[str, str]


user = User(
    name="John",
    surname="Doe",
    age=30,
    email="john.doe@example.com",
    phone="123-456-7890",
    social_accounts={"bluesky": "john.doe", "instagram": "johndoe1234"},
)

display(Markdown(prompt.format(data=user)))

```

# Using a BaseModel from pydantic import BaseModel from typing import Dict from IPython.display import Markdown, display class User(BaseModel): name: str surname: str age: int email: str phone: str social_accounts: Dict[str, str] user = User( name="John", surname="Doe", age=30, email="john.doe@example.com", phone="123-456-7890", social_accounts={"bluesky": "john.doe", "instagram": "johndoe1234"}, ) display(Markdown(prompt.format(data=user)))
Please extract from the following XML code the contact details of the user:
```
<user>
	<name>John</name>
	<surname>Doe</surname>
	<age>30</age>
	<email>john.doe@example.com</email>
	<phone>123-456-7890</phone>
	<social_accounts>{'bluesky': 'john.doe', 'instagram': 'johndoe1234'}</social_accounts>
</user>

```

In [ ]:
Copied!
```
# with a dictionary

user_dict = {
    "name": "John",
    "surname": "Doe",
    "age": 30,
    "email": "john.doe@example.com",
    "phone": "123-456-7890",
    "social_accounts": {"bluesky": "john.doe", "instagram": "johndoe1234"},
}

display(Markdown(prompt.format(data=user_dict)))

```

# with a dictionary user_dict = { "name": "John", "surname": "Doe", "age": 30, "email": "john.doe@example.com", "phone": "123-456-7890", "social_accounts": {"bluesky": "john.doe", "instagram": "johndoe1234"}, } display(Markdown(prompt.format(data=user_dict)))
Please extract from the following XML code the contact details of the user:
```
<input>
	<name>John</name>
	<surname>Doe</surname>
	<age>30</age>
	<email>john.doe@example.com</email>
	<phone>123-456-7890</phone>
	<social_accounts>{'bluesky': 'john.doe', 'instagram': 'johndoe1234'}</social_accounts>
</input>

```

In [ ]:
Copied!
```
# Using a JSON-like string

user_str = '{"name":"John","surname":"Doe","age":30,"email":"john.doe@example.com","phone":"123-456-7890","social_accounts":{"bluesky":"john.doe","instagram":"johndoe1234"}}'

display(Markdown(prompt.format(data=user_str)))

```

# Using a JSON-like string user_str = '{"name":"John","surname":"Doe","age":30,"email":"john.doe@example.com","phone":"123-456-7890","social_accounts":{"bluesky":"john.doe","instagram":"johndoe1234"}}' display(Markdown(prompt.format(data=user_str)))
Please extract from the following XML code the contact details of the user:
```
<input>
	<name>John</name>
	<surname>Doe</surname>
	<age>30</age>
	<email>john.doe@example.com</email>
	<phone>123-456-7890</phone>
	<social_accounts>{'bluesky': 'john.doe', 'instagram': 'johndoe1234'}</social_accounts>
</input>

```

### 3. Chat With an LLM¶
Now that we know how to produce structured input, let's employ it to chat with an LLM!
In [ ]:
Copied!
```
import os
from getpass import getpass

os.environ["OPENAI_API_KEY"] = getpass()

```

import os from getpass import getpass os.environ["OPENAI_API_KEY"] = getpass()
```
··········

```

In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI

llm = OpenAI(model="gpt-4.1-mini")

response = await llm.achat(prompt.format_messages(data=user))

```

from llama_index.llms.openai import OpenAI llm = OpenAI(model="gpt-4.1-mini") response = await llm.achat(prompt.format_messages(data=user))
In [ ]:
Copied!
```
print(response.message.content)

```

print(response.message.content)
```
The contact details of the user are:

- Email: john.doe@example.com  
- Phone: 123-456-7890  
- Social Accounts:  
  - Bluesky: john.doe  
  - Instagram: johndoe1234

```

### 4. Use Structured Input and Structured Output¶
Combining structured input and structured output might really help to boost the reliability of the outputs of your LLMs - so let's give it a go!
In [ ]:
Copied!
```
from pydantic import Field
from typing import Optional


class SocialAccounts(BaseModel):
    instagram: Optional[str] = Field(default=None)
    bluesky: Optional[str] = Field(default=None)
    x: Optional[str] = Field(default=None)
    mastodon: Optional[str] = Field(default=None)


class ContactDetails(BaseModel):
    email: str
    phone: str
    social_accounts: SocialAccounts

```

from pydantic import Field from typing import Optional class SocialAccounts(BaseModel): instagram: Optional[str] = Field(default=None) bluesky: Optional[str] = Field(default=None) x: Optional[str] = Field(default=None) mastodon: Optional[str] = Field(default=None) class ContactDetails(BaseModel): email: str phone: str social_accounts: SocialAccounts
In [ ]:
Copied!
```
sllm = llm.as_structured_llm(ContactDetails)

```

sllm = llm.as_structured_llm(ContactDetails)
In [ ]:
Copied!
```
structured_response = await sllm.achat(prompt.format_messages(data=user))

```

structured_response = await sllm.achat(prompt.format_messages(data=user))
In [ ]:
Copied!
```
print(structured_response.raw.email)
print(structured_response.raw.phone)
print(structured_response.raw.social_accounts.instagram)
print(structured_response.raw.social_accounts.bluesky)

```

print(structured_response.raw.email) print(structured_response.raw.phone) print(structured_response.raw.social_accounts.instagram) print(structured_response.raw.social_accounts.bluesky)
```
john.doe@example.com
123-456-7890
johndoe1234
john.doe

```

