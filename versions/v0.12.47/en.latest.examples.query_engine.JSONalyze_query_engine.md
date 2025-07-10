![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# JSONalyze Query Engine¶
JSONalyze, or JSON Analyze Query Engine is designed to be wired typically after a calling(by agent, etc) of APIs, where we have the returned value as bulk instances of rows, and the next step is to perform statistical analysis on the data.
With JSONalyze, under the hood, in-memory SQLite table is created with the JSON List loaded, the query engine is able to perform SQL queries on the data, and return the Query Result as answer to the analytical questions.
This is a very simple example of how to use JSONalyze Query Engine.
First let's install llama-index.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai

```

%pip install llama-index-llms-openai
In [ ]:
Copied!
```
%pip install llama-index

```

%pip install llama-index
In [ ]:
Copied!
```
# JSONalyze Query Engine rely on sqlite-utils
%pip install sqlite-utils

```

# JSONalyze Query Engine rely on sqlite-utils %pip install sqlite-utils
In [ ]:
Copied!
```
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

```

import logging import sys logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
In [ ]:
Copied!
```
import os
import openai

os.environ["OPENAI_API_KEY"] = "YOUR_KEY_HERE"
openai.api_key = os.environ["OPENAI_API_KEY"]

```

import os import openai os.environ["OPENAI_API_KEY"] = "YOUR_KEY_HERE" openai.api_key = os.environ["OPENAI_API_KEY"]
In [ ]:
Copied!
```
from IPython.display import Markdown, display

```

from IPython.display import Markdown, display
Let's assume we have a list of JSON(already loaded as List of Dicts) as follows:
In [ ]:
Copied!
```
json_list = [
    {
        "name": "John Doe",
        "age": 25,
        "major": "Computer Science",
        "email": "john.doe@example.com",
        "address": "123 Main St",
        "city": "New York",
        "state": "NY",
        "country": "USA",
        "phone": "+1 123-456-7890",
        "occupation": "Software Engineer",
    },
    {
        "name": "Jane Smith",
        "age": 30,
        "major": "Business Administration",
        "email": "jane.smith@example.com",
        "address": "456 Elm St",
        "city": "San Francisco",
        "state": "CA",
        "country": "USA",
        "phone": "+1 234-567-8901",
        "occupation": "Marketing Manager",
    },
    {
        "name": "Michael Johnson",
        "age": 35,
        "major": "Finance",
        "email": "michael.johnson@example.com",
        "address": "789 Oak Ave",
        "city": "Chicago",
        "state": "IL",
        "country": "USA",
        "phone": "+1 345-678-9012",
        "occupation": "Financial Analyst",
    },
    {
        "name": "Emily Davis",
        "age": 28,
        "major": "Psychology",
        "email": "emily.davis@example.com",
        "address": "234 Pine St",
        "city": "Los Angeles",
        "state": "CA",
        "country": "USA",
        "phone": "+1 456-789-0123",
        "occupation": "Psychologist",
    },
    {
        "name": "Alex Johnson",
        "age": 27,
        "major": "Engineering",
        "email": "alex.johnson@example.com",
        "address": "567 Cedar Ln",
        "city": "Seattle",
        "state": "WA",
        "country": "USA",
        "phone": "+1 567-890-1234",
        "occupation": "Civil Engineer",
    },
    {
        "name": "Jessica Williams",
        "age": 32,
        "major": "Biology",
        "email": "jessica.williams@example.com",
        "address": "890 Walnut Ave",
        "city": "Boston",
        "state": "MA",
        "country": "USA",
        "phone": "+1 678-901-2345",
        "occupation": "Biologist",
    },
    {
        "name": "Matthew Brown",
        "age": 26,
        "major": "English Literature",
        "email": "matthew.brown@example.com",
        "address": "123 Peach St",
        "city": "Atlanta",
        "state": "GA",
        "country": "USA",
        "phone": "+1 789-012-3456",
        "occupation": "Writer",
    },
    {
        "name": "Olivia Wilson",
        "age": 29,
        "major": "Art",
        "email": "olivia.wilson@example.com",
        "address": "456 Plum Ave",
        "city": "Miami",
        "state": "FL",
        "country": "USA",
        "phone": "+1 890-123-4567",
        "occupation": "Artist",
    },
    {
        "name": "Daniel Thompson",
        "age": 31,
        "major": "Physics",
        "email": "daniel.thompson@example.com",
        "address": "789 Apple St",
        "city": "Denver",
        "state": "CO",
        "country": "USA",
        "phone": "+1 901-234-5678",
        "occupation": "Physicist",
    },
    {
        "name": "Sophia Clark",
        "age": 27,
        "major": "Sociology",
        "email": "sophia.clark@example.com",
        "address": "234 Orange Ln",
        "city": "Austin",
        "state": "TX",
        "country": "USA",
        "phone": "+1 012-345-6789",
        "occupation": "Social Worker",
    },
    {
        "name": "Christopher Lee",
        "age": 33,
        "major": "Chemistry",
        "email": "christopher.lee@example.com",
        "address": "567 Mango St",
        "city": "San Diego",
        "state": "CA",
        "country": "USA",
        "phone": "+1 123-456-7890",
        "occupation": "Chemist",
    },
    {
        "name": "Ava Green",
        "age": 28,
        "major": "History",
        "email": "ava.green@example.com",
        "address": "890 Cherry Ave",
        "city": "Philadelphia",
        "state": "PA",
        "country": "USA",
        "phone": "+1 234-567-8901",
        "occupation": "Historian",
    },
    {
        "name": "Ethan Anderson",
        "age": 30,
        "major": "Business",
        "email": "ethan.anderson@example.com",
        "address": "123 Lemon Ln",
        "city": "Houston",
        "state": "TX",
        "country": "USA",
        "phone": "+1 345-678-9012",
        "occupation": "Entrepreneur",
    },
    {
        "name": "Isabella Carter",
        "age": 28,
        "major": "Mathematics",
        "email": "isabella.carter@example.com",
        "address": "456 Grape St",
        "city": "Phoenix",
        "state": "AZ",
        "country": "USA",
        "phone": "+1 456-789-0123",
        "occupation": "Mathematician",
    },
    {
        "name": "Andrew Walker",
        "age": 32,
        "major": "Economics",
        "email": "andrew.walker@example.com",
        "address": "789 Berry Ave",
        "city": "Portland",
        "state": "OR",
        "country": "USA",
        "phone": "+1 567-890-1234",
        "occupation": "Economist",
    },
    {
        "name": "Mia Evans",
        "age": 29,
        "major": "Political Science",
        "email": "mia.evans@example.com",
        "address": "234 Lime St",
        "city": "Washington",
        "state": "DC",
        "country": "USA",
        "phone": "+1 678-901-2345",
        "occupation": "Political Analyst",
    },
]

```

json_list = [ { "name": "John Doe", "age": 25, "major": "Computer Science", "email": "john.doe@example.com", "address": "123 Main St", "city": "New York", "state": "NY", "country": "USA", "phone": "+1 123-456-7890", "occupation": "Software Engineer", }, { "name": "Jane Smith", "age": 30, "major": "Business Administration", "email": "jane.smith@example.com", "address": "456 Elm St", "city": "San Francisco", "state": "CA", "country": "USA", "phone": "+1 234-567-8901", "occupation": "Marketing Manager", }, { "name": "Michael Johnson", "age": 35, "major": "Finance", "email": "michael.johnson@example.com", "address": "789 Oak Ave", "city": "Chicago", "state": "IL", "country": "USA", "phone": "+1 345-678-9012", "occupation": "Financial Analyst", }, { "name": "Emily Davis", "age": 28, "major": "Psychology", "email": "emily.davis@example.com", "address": "234 Pine St", "city": "Los Angeles", "state": "CA", "country": "USA", "phone": "+1 456-789-0123", "occupation": "Psychologist", }, { "name": "Alex Johnson", "age": 27, "major": "Engineering", "email": "alex.johnson@example.com", "address": "567 Cedar Ln", "city": "Seattle", "state": "WA", "country": "USA", "phone": "+1 567-890-1234", "occupation": "Civil Engineer", }, { "name": "Jessica Williams", "age": 32, "major": "Biology", "email": "jessica.williams@example.com", "address": "890 Walnut Ave", "city": "Boston", "state": "MA", "country": "USA", "phone": "+1 678-901-2345", "occupation": "Biologist", }, { "name": "Matthew Brown", "age": 26, "major": "English Literature", "email": "matthew.brown@example.com", "address": "123 Peach St", "city": "Atlanta", "state": "GA", "country": "USA", "phone": "+1 789-012-3456", "occupation": "Writer", }, { "name": "Olivia Wilson", "age": 29, "major": "Art", "email": "olivia.wilson@example.com", "address": "456 Plum Ave", "city": "Miami", "state": "FL", "country": "USA", "phone": "+1 890-123-4567", "occupation": "Artist", }, { "name": "Daniel Thompson", "age": 31, "major": "Physics", "email": "daniel.thompson@example.com", "address": "789 Apple St", "city": "Denver", "state": "CO", "country": "USA", "phone": "+1 901-234-5678", "occupation": "Physicist", }, { "name": "Sophia Clark", "age": 27, "major": "Sociology", "email": "sophia.clark@example.com", "address": "234 Orange Ln", "city": "Austin", "state": "TX", "country": "USA", "phone": "+1 012-345-6789", "occupation": "Social Worker", }, { "name": "Christopher Lee", "age": 33, "major": "Chemistry", "email": "christopher.lee@example.com", "address": "567 Mango St", "city": "San Diego", "state": "CA", "country": "USA", "phone": "+1 123-456-7890", "occupation": "Chemist", }, { "name": "Ava Green", "age": 28, "major": "History", "email": "ava.green@example.com", "address": "890 Cherry Ave", "city": "Philadelphia", "state": "PA", "country": "USA", "phone": "+1 234-567-8901", "occupation": "Historian", }, { "name": "Ethan Anderson", "age": 30, "major": "Business", "email": "ethan.anderson@example.com", "address": "123 Lemon Ln", "city": "Houston", "state": "TX", "country": "USA", "phone": "+1 345-678-9012", "occupation": "Entrepreneur", }, { "name": "Isabella Carter", "age": 28, "major": "Mathematics", "email": "isabella.carter@example.com", "address": "456 Grape St", "city": "Phoenix", "state": "AZ", "country": "USA", "phone": "+1 456-789-0123", "occupation": "Mathematician", }, { "name": "Andrew Walker", "age": 32, "major": "Economics", "email": "andrew.walker@example.com", "address": "789 Berry Ave", "city": "Portland", "state": "OR", "country": "USA", "phone": "+1 567-890-1234", "occupation": "Economist", }, { "name": "Mia Evans", "age": 29, "major": "Political Science", "email": "mia.evans@example.com", "address": "234 Lime St", "city": "Washington", "state": "DC", "country": "USA", "phone": "+1 678-901-2345", "occupation": "Political Analyst", }, ]
Then, we can create a JSONalyze Query Engine instance, with the JSON List as input.
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import JSONalyzeQueryEngine

llm = OpenAI(model="gpt-3.5-turbo")

json_stats_query_engine = JSONalyzeQueryEngine(
    list_of_dict=json_list,
    llm=llm,
    verbose=True,
)

```

from llama_index.llms.openai import OpenAI from llama_index.core.query_engine import JSONalyzeQueryEngine llm = OpenAI(model="gpt-3.5-turbo") json_stats_query_engine = JSONalyzeQueryEngine( list_of_dict=json_list, llm=llm, verbose=True, )
```
INFO:numexpr.utils:NumExpr defaulting to 8 threads.
NumExpr defaulting to 8 threads.

```

To demonstrate the Query Engine, let's first create a list of stastical questions, and then we can use the Query Engine to answer the questions.
In [ ]:
Copied!
```
questions = [
    "What is the average age of the individuals in the dataset?",
    "What is the maximum age among the individuals?",
    "What is the minimum age among the individuals?",
    "How many individuals have a major in Psychology?",
    "What is the most common major among the individuals?",
    "What is the percentage of individuals residing in California (CA)?",
    "How many individuals have an occupation related to science or engineering?",
    "What is the average length of the email addresses in the dataset?",
    "How many individuals have a phone number starting with '+1 234'?",
    "What is the distribution of ages among the individuals?",
]

```

questions = [ "What is the average age of the individuals in the dataset?", "What is the maximum age among the individuals?", "What is the minimum age among the individuals?", "How many individuals have a major in Psychology?", "What is the most common major among the individuals?", "What is the percentage of individuals residing in California (CA)?", "How many individuals have an occupation related to science or engineering?", "What is the average length of the email addresses in the dataset?", "How many individuals have a phone number starting with '+1 234'?", "What is the distribution of ages among the individuals?", ]
Say we want to know the average of the age of the people in the list, we can use the following query:
In [ ]:
Copied!
```
display(
    Markdown("> Question: {}".format(questions[0])),
    Markdown("Answer: {}".format(json_stats_query_engine.query(questions[0]))),
)

```

display( Markdown("> Question: {}".format(questions[0])), Markdown("Answer: {}".format(json_stats_query_engine.query(questions[0]))), )
```
Query: What is the average age of the individuals in the dataset?
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
SQL Query: SELECT AVG(age) FROM items
Table Schema: {'name': <class 'str'>, 'age': <class 'int'>, 'major': <class 'str'>, 'email': <class 'str'>, 'address': <class 'str'>, 'city': <class 'str'>, 'state': <class 'str'>, 'country': <class 'str'>, 'phone': <class 'str'>, 'occupation': <class 'str'>}
SQL Response: [{'AVG(age)': 29.375}]
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
Response: The average age of the individuals in the dataset is 29.375.
```

> Question: What is the average age of the individuals in the dataset?
Answer: The average age of the individuals in the dataset is 29.375.
We can also use the Query Engine to answer other questions:
In [ ]:
Copied!
```
display(
    Markdown("> Question: {}".format(questions[4])),
    Markdown("Answer: {}".format(json_stats_query_engine.query(questions[4]))),
)

```

display( Markdown("> Question: {}".format(questions[4])), Markdown("Answer: {}".format(json_stats_query_engine.query(questions[4]))), )
```
Query: What is the most common major among the individuals?
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
SQL Query: SELECT major, COUNT(*) as count
FROM items
GROUP BY major
ORDER BY count DESC
LIMIT 1;
Table Schema: {'name': <class 'str'>, 'age': <class 'int'>, 'major': <class 'str'>, 'email': <class 'str'>, 'address': <class 'str'>, 'city': <class 'str'>, 'state': <class 'str'>, 'country': <class 'str'>, 'phone': <class 'str'>, 'occupation': <class 'str'>}
SQL Response: [{'major': 'Sociology', 'count': 1}]
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
Response: The most common major among the individuals is Sociology.
```

> Question: What is the most common major among the individuals?
Answer: The most common major among the individuals is Sociology.
In [ ]:
Copied!
```
display(
    Markdown("> Question: {}".format(questions[7])),
    Markdown("Answer: {}".format(json_stats_query_engine.query(questions[7]))),
)

```

display( Markdown("> Question: {}".format(questions[7])), Markdown("Answer: {}".format(json_stats_query_engine.query(questions[7]))), )
```
Query: What is the average length of the email addresses in the dataset?
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
SQL Query: SELECT AVG(LENGTH(email)) FROM items
Table Schema: {'name': <class 'str'>, 'age': <class 'int'>, 'major': <class 'str'>, 'email': <class 'str'>, 'address': <class 'str'>, 'city': <class 'str'>, 'state': <class 'str'>, 'country': <class 'str'>, 'phone': <class 'str'>, 'occupation': <class 'str'>}
SQL Response: [{'AVG(LENGTH(email))': 24.5}]
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
Response: The average length of the email addresses in the dataset is 24.5 characters.
```

> Question: What is the average length of the email addresses in the dataset?
Answer: The average length of the email addresses in the dataset is 24.5 characters.
In [ ]:
Copied!
```
display(
    Markdown("> Question: {}".format(questions[5])),
    Markdown("Answer: {}".format(json_stats_query_engine.query(questions[5]))),
)

```

display( Markdown("> Question: {}".format(questions[5])), Markdown("Answer: {}".format(json_stats_query_engine.query(questions[5]))), )
```
Query: What is the percentage of individuals residing in California (CA)?
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
SQL Query: SELECT (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM items)) AS percentage
FROM items
WHERE state = 'CA'
Table Schema: {'name': <class 'str'>, 'age': <class 'int'>, 'major': <class 'str'>, 'email': <class 'str'>, 'address': <class 'str'>, 'city': <class 'str'>, 'state': <class 'str'>, 'country': <class 'str'>, 'phone': <class 'str'>, 'occupation': <class 'str'>}
SQL Response: [{'percentage': 18.75}]
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
Response: The percentage of individuals residing in California (CA) is 18.75%.
```

> Question: What is the percentage of individuals residing in California (CA)?
Answer: The percentage of individuals residing in California (CA) is 18.75%.
In [ ]:
Copied!
```
display(
    Markdown("> Question: {}".format(questions[9])),
    Markdown("Answer: {}".format(json_stats_query_engine.query(questions[9]))),
)

```

display( Markdown("> Question: {}".format(questions[9])), Markdown("Answer: {}".format(json_stats_query_engine.query(questions[9]))), )
```
Query: What is the distribution of ages among the individuals?
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
SQL Query: SELECT age, COUNT(*) as count
FROM items
GROUP BY age
Table Schema: {'name': <class 'str'>, 'age': <class 'int'>, 'major': <class 'str'>, 'email': <class 'str'>, 'address': <class 'str'>, 'city': <class 'str'>, 'state': <class 'str'>, 'country': <class 'str'>, 'phone': <class 'str'>, 'occupation': <class 'str'>}
SQL Response: [{'age': 25, 'count': 1}, {'age': 26, 'count': 1}, {'age': 27, 'count': 2}, {'age': 28, 'count': 3}, {'age': 29, 'count': 2}, {'age': 30, 'count': 2}, {'age': 31, 'count': 1}, {'age': 32, 'count': 2}, {'age': 33, 'count': 1}, {'age': 35, 'count': 1}]
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
Response: The distribution of ages among the individuals is as follows:
- 1 individual is 25 years old
- 1 individual is 26 years old
- 2 individuals are 27 years old
- 3 individuals are 28 years old
- 2 individuals are 29 years old
- 2 individuals are 30 years old
- 1 individual is 31 years old
- 2 individuals are 32 years old
- 1 individual is 33 years old
- 1 individual is 35 years old
```

> Question: What is the distribution of ages among the individuals?
Answer: The distribution of ages among the individuals is as follows:
  * 1 individual is 25 years old
  * 1 individual is 26 years old
  * 2 individuals are 27 years old
  * 3 individuals are 28 years old
  * 2 individuals are 29 years old
  * 2 individuals are 30 years old
  * 1 individual is 31 years old
  * 2 individuals are 32 years old
  * 1 individual is 33 years old
  * 1 individual is 35 years old


In [ ]:
Copied!
```
# e2e test async

json_stats_aquery_engine = JSONalyzeQueryEngine(
    list_of_dict=json_list,
    llm=llm,
    verbose=True,
    use_async=True,
)

```

# e2e test async json_stats_aquery_engine = JSONalyzeQueryEngine( list_of_dict=json_list, llm=llm, verbose=True, use_async=True, )
In [ ]:
Copied!
```
display(
    Markdown("> Question: {}".format(questions[7])),
    Markdown("Answer: {}".format(json_stats_query_engine.query(questions[7]))),
)

```

display( Markdown("> Question: {}".format(questions[7])), Markdown("Answer: {}".format(json_stats_query_engine.query(questions[7]))), )
```
Query: What is the average length of the email addresses in the dataset?
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
SQL Query: SELECT AVG(LENGTH(email)) FROM items
Table Schema: {'name': <class 'str'>, 'age': <class 'int'>, 'major': <class 'str'>, 'email': <class 'str'>, 'address': <class 'str'>, 'city': <class 'str'>, 'state': <class 'str'>, 'country': <class 'str'>, 'phone': <class 'str'>, 'occupation': <class 'str'>}
SQL Response: [{'AVG(LENGTH(email))': 24.5}]
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
Response: The average length of the email addresses in the dataset is 24.5 characters.
```

> Question: What is the average length of the email addresses in the dataset?
Answer: The average length of the email addresses in the dataset is 24.5 characters.
