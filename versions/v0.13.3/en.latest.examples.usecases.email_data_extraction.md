![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Email Data Extraction¶
OpenAI functions can be used to extract data from Email. This is another example of getting structured data from unstructured conent using LLamaIndex.
The primary objective of this example is to transform raw email content into an easily interpretable JSON format, exemplifying a practical application of language models in data extraction. Extracted structued JSON data can then be used in any downstream application.
We will use a sample email as shown in below image. This email mimics a typical daily communication sent by ARK Investment to its subscribers. This sample email includes detailed information about trades under their Exchange-Traded Funds (ETFs). By using this specific example, we aim to showcase how we can effectively extract and structure complex financial data from a real-world email scenario, transforming it into a comprehensible JSON format
![Ark Daily Trades](https://docs.llamaindex.ai/en/latest/examples/usecases/data/images/ark_email_sample.PNG)
### Add required packages¶
You will need following libraries along with LlamaIndex 🦙.
  * `unstructured[msg]`: A package for handling unstructured data, required to get content from `.eml` and `.msg` format.


In [ ]:
Copied!
```
%pip install llama-index-llms-openai
%pip install llama-index-readers-file
%pip install llama-index-program-openai

```

%pip install llama-index-llms-openai %pip install llama-index-readers-file %pip install llama-index-program-openai
In [ ]:
Copied!
```
# LlamaIndex
!pip install llama-index

# To get text conents from .eml and .msg file
!pip install "unstructured[msg]"

```

# LlamaIndex !pip install llama-index # To get text conents from .eml and .msg file !pip install "unstructured[msg]"
### Enable Logging and Set up OpenAI API Key¶
In this step, we set up logging to monitor the program's execution and debug if needed. We also configure the OpenAI API key, essential for utilizing OpenAI services. Replace "YOUR_KEY_HERE" with your actual OpenAI API key.
In [ ]:
Copied!
```
import logging
import sys, json

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

```

import logging import sys, json logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
In [ ]:
Copied!
```
import os
import openai

# os.environ["OPENAI_API_KEY"] = "YOUR_KEY_HERE"
openai.api_key = os.environ["OPENAI_API_KEY"]

```

import os import openai # os.environ["OPENAI_API_KEY"] = "YOUR_KEY_HERE" openai.api_key = os.environ["OPENAI_API_KEY"]
### Set Up Expected JSON Output Definition (JSON Schema)¶
Here we define a Python class named `EmailData` using the Pydantic library. This class models the structure of the data we expect to extract from emails, including sender, receiver, the date and time of the email, etfs having list of shares traded under that ETF.
In [ ]:
Copied!
```
from pydantic import BaseModel, Field
from typing import List


class Instrument(BaseModel):
    """Datamodel for ticker trading details."""

    direction: str = Field(description="ticker trading - Buy, Sell, Hold etc")
    ticker: str = Field(
        description="Stock Ticker. 1-4 character code. Example: AAPL, TSLS, MSFT, VZ"
    )
    company_name: str = Field(
        description="Company name corresponding to ticker"
    )
    shares_traded: float = Field(description="Number of shares traded")
    percent_of_etf: float = Field(description="Percentage of ETF")


class Etf(BaseModel):
    """ETF trading data model"""

    etf_ticker: str = Field(
        description="ETF Ticker code. Example: ARKK, FSPTX"
    )
    trade_date: str = Field(description="Date of trading")
    stocks: List[Instrument] = Field(
        description="List of instruments or shares traded under this etf"
    )


class EmailData(BaseModel):
    """Data model for email extracted information."""

    etfs: List[Etf] = Field(
        description="List of ETFs described in email having list of shares traded under it"
    )
    trade_notification_date: str = Field(
        description="Date of trade notification"
    )
    sender_email_id: str = Field(description="Email Id of the email sender.")
    email_date_time: str = Field(description="Date and time of email")

```

from pydantic import BaseModel, Field from typing import List class Instrument(BaseModel): """Datamodel for ticker trading details.""" direction: str = Field(description="ticker trading - Buy, Sell, Hold etc") ticker: str = Field( description="Stock Ticker. 1-4 character code. Example: AAPL, TSLS, MSFT, VZ" ) company_name: str = Field( description="Company name corresponding to ticker" ) shares_traded: float = Field(description="Number of shares traded") percent_of_etf: float = Field(description="Percentage of ETF") class Etf(BaseModel): """ETF trading data model""" etf_ticker: str = Field( description="ETF Ticker code. Example: ARKK, FSPTX" ) trade_date: str = Field(description="Date of trading") stocks: List[Instrument] = Field( description="List of instruments or shares traded under this etf" ) class EmailData(BaseModel): """Data model for email extracted information.""" etfs: List[Etf] = Field( description="List of ETFs described in email having list of shares traded under it" ) trade_notification_date: str = Field( description="Date of trade notification" ) sender_email_id: str = Field(description="Email Id of the email sender.") email_date_time: str = Field(description="Date and time of email")
### Load content from .eml / .msg file¶
In this step, we will use the `UnstructuredReader` from the `llama-hub` to load the content of an .eml email file or .msg Outlook file. This file's contents are then stored in a variable for further processing.
In [ ]:
Copied!
```
# get donload_loader
from llama_index.core import download_loader

```

# get donload_loader from llama_index.core import download_loader
In [ ]:
Copied!
```
# Create a download loader
from llama_index.readers.file import UnstructuredReader

# Initialize the UnstructuredReader
loader = UnstructuredReader()

# For eml file
eml_documents = loader.load_data("../data/email/ark-trading-jan-12-2024.eml")
email_content = eml_documents[0].text
print("\n\n Email contents")
print(email_content)

```

# Create a download loader from llama_index.readers.file import UnstructuredReader # Initialize the UnstructuredReader loader = UnstructuredReader() # For eml file eml_documents = loader.load_data("../data/email/ark-trading-jan-12-2024.eml") email_content = eml_documents[0].text print("\n\n Email contents") print(email_content)
In [ ]:
Copied!
```
# For Outlook msg
msg_documents = loader.load_data("../data/email/ark-trading-jan-12-2024.msg")
msg_content = msg_documents[0].text
print("\n\n Outlook contents")
print(msg_content)

```

# For Outlook msg msg_documents = loader.load_data("../data/email/ark-trading-jan-12-2024.msg") msg_content = msg_documents[0].text print("\n\n Outlook contents") print(msg_content)
### Use LLM function to extract content in JSON format¶
In the final step, we utilize the `llama_index` package to create a prompt template for extracting insights from the loaded email. An instance of the `OpenAI` model is used to interpret the email content and extract the relevant information based on our predefined `EmailData` schema. The output is then converted to a dictionary format for easy viewing and processing.
In [ ]:
Copied!
```
from llama_index.program.openai import OpenAIPydanticProgram
from llama_index.core import ChatPromptTemplate
from llama_index.core.llms import ChatMessage
from llama_index.llms.openai import OpenAI

```

from llama_index.program.openai import OpenAIPydanticProgram from llama_index.core import ChatPromptTemplate from llama_index.core.llms import ChatMessage from llama_index.llms.openai import OpenAI
In [ ]:
Copied!
```
prompt = ChatPromptTemplate(
    message_templates=[
        ChatMessage(
            role="system",
            content=(
                "You are an expert assitant for extracting insights from email in JSON format. \n"
                "You extract data and returns it in JSON format, according to provided JSON schema, from given email message. \n"
                "REMEMBER to return extracted data only from provided email message."
            ),
        ),
        ChatMessage(
            role="user",
            content=(
                "Email Message: \n" "------\n" "{email_msg_content}\n" "------"
            ),
        ),
    ]
)

llm = OpenAI(model="gpt-3.5-turbo-1106")

program = OpenAIPydanticProgram.from_defaults(
    output_cls=EmailData,
    llm=llm,
    prompt=prompt,
    verbose=True,
)

```

prompt = ChatPromptTemplate( message_templates=[ ChatMessage( role="system", content=( "You are an expert assitant for extracting insights from email in JSON format. \n" "You extract data and returns it in JSON format, according to provided JSON schema, from given email message. \n" "REMEMBER to return extracted data only from provided email message." ), ), ChatMessage( role="user", content=( "Email Message: \n" "------\n" "{email_msg_content}\n" "------" ), ), ] ) llm = OpenAI(model="gpt-3.5-turbo-1106") program = OpenAIPydanticProgram.from_defaults( output_cls=EmailData, llm=llm, prompt=prompt, verbose=True, )
In [ ]:
Copied!
```
output = program(email_msg_content=email_content)
print("Output JSON From .eml File: ")
print(json.dumps(output.dict(), indent=2))

```

output = program(email_msg_content=email_content) print("Output JSON From .eml File: ") print(json.dumps(output.dict(), indent=2))
```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
Function call: EmailData with args: {"etfs":[{"etf_ticker":"ARKK","trade_date":"1/12/2024","stocks":[{"direction":"Buy","ticker":"TSLA","company_name":"TESLA INC","shares_traded":93654,"percent_of_etf":0.2453},{"direction":"Buy","ticker":"TXG","company_name":"10X GENOMICS INC","shares_traded":159506,"percent_of_etf":0.0907},{"direction":"Buy","ticker":"CRSP","company_name":"CRISPR THERAPEUTICS AG","shares_traded":86268,"percent_of_etf":0.0669},{"direction":"Buy","ticker":"RXRX","company_name":"RECURSION PHARMACEUTICALS","shares_traded":289619,"percent_of_etf":0.0391},{"direction":"Sell","ticker":"HOOD","company_name":"ROBINHOOD MARKETS INC","shares_traded":927,"percent_of_etf":0.0001},{"direction":"Sell","ticker":"EXAS","company_name":"EXACT SCIENCES CORP","shares_traded":100766,"percent_of_etf":0.0829},{"direction":"Sell","ticker":"TWLO","company_name":"TWILIO INC","shares_traded":108523,"percent_of_etf":0.0957},{"direction":"Sell","ticker":"PD","company_name":"PAGERDUTY INC","shares_traded":302096,"percent_of_etf":0.0958},{"direction":"Sell","ticker":"PATH","company_name":"UIPATH INC","shares_traded":553172,"percent_of_etf":0.1476}],"trade_date":"1/12/2024"},{"etf_ticker":"ARKW","trade_date":"1/12/2024","stocks":[{"direction":"Buy","ticker":"TSLA","company_name":"TESLA INC","shares_traded":18148,"percent_of_etf":0.2454},{"direction":"Sell","ticker":"HOOD","company_name":"ROBINHOOD MARKETS INC","shares_traded":49,"percent_of_etf":0.0000},{"direction":"Sell","ticker":"PD","company_name":"PAGERDUTY INC","shares_traded":9756,"percent_of_etf":0.016},{"direction":"Sell","ticker":"TWLO","company_name":"TWILIO INC","shares_traded":21849,"percent_of_etf":0.0994},{"direction":"Sell","ticker":"PATH","company_name":"UIPATH INC","shares_traded":105944,"percent_of_etf":0.1459}],"trade_date":"1/12/2024"},{"etf_ticker":"ARKG","trade_date":"1/12/2024","stocks":[{"direction":"Buy","ticker":"TXG","company_name":"10X GENOMICS INC","shares_traded":38042,"percent_of_etf":0.0864},{"direction":"Buy","ticker":"CRSP","company_name":"CRISPR THERAPEUTICS AG","shares_traded":21197,"percent_of_etf":0.0656},{"direction":"Buy","ticker":"RXRX","company_name":"RECURSION PHARMACEUTICALS","shares_traded":67422,"percent_of_etf":0.0363},{"direction":"Buy","ticker":"RPTX","company_name":"REPARE THERAPEUTICS INC","shares_traded":15410,"percent_of_etf":0.0049},{"direction":"Sell","ticker":"EXAS","company_name":"EXACT SCIENCES CORP","shares_traded":32057,"percent_of_etf":0.1052}],"trade_date":"1/12/2024"}],"trade_notification_date":"1/12/2024","sender_email_id":"ark@ark-funds.com","email_date_time":"1/12/2024"}
Output JSON From .eml File: 
{
  "etfs": [
    {
      "etf_ticker": "ARKK",
      "trade_date": "1/12/2024",
      "stocks": [
        {
          "direction": "Buy",
          "ticker": "TSLA",
          "company_name": "TESLA INC",
          "shares_traded": 93654.0,
          "percent_of_etf": 0.2453
        },
        {
          "direction": "Buy",
          "ticker": "TXG",
          "company_name": "10X GENOMICS INC",
          "shares_traded": 159506.0,
          "percent_of_etf": 0.0907
        },
        {
          "direction": "Buy",
          "ticker": "CRSP",
          "company_name": "CRISPR THERAPEUTICS AG",
          "shares_traded": 86268.0,
          "percent_of_etf": 0.0669
        },
        {
          "direction": "Buy",
          "ticker": "RXRX",
          "company_name": "RECURSION PHARMACEUTICALS",
          "shares_traded": 289619.0,
          "percent_of_etf": 0.0391
        },
        {
          "direction": "Sell",
          "ticker": "HOOD",
          "company_name": "ROBINHOOD MARKETS INC",
          "shares_traded": 927.0,
          "percent_of_etf": 0.0001
        },
        {
          "direction": "Sell",
          "ticker": "EXAS",
          "company_name": "EXACT SCIENCES CORP",
          "shares_traded": 100766.0,
          "percent_of_etf": 0.0829
        },
        {
          "direction": "Sell",
          "ticker": "TWLO",
          "company_name": "TWILIO INC",
          "shares_traded": 108523.0,
          "percent_of_etf": 0.0957
        },
        {
          "direction": "Sell",
          "ticker": "PD",
          "company_name": "PAGERDUTY INC",
          "shares_traded": 302096.0,
          "percent_of_etf": 0.0958
        },
        {
          "direction": "Sell",
          "ticker": "PATH",
          "company_name": "UIPATH INC",
          "shares_traded": 553172.0,
          "percent_of_etf": 0.1476
        }
      ]
    },
    {
      "etf_ticker": "ARKW",
      "trade_date": "1/12/2024",
      "stocks": [
        {
          "direction": "Buy",
          "ticker": "TSLA",
          "company_name": "TESLA INC",
          "shares_traded": 18148.0,
          "percent_of_etf": 0.2454
        },
        {
          "direction": "Sell",
          "ticker": "HOOD",
          "company_name": "ROBINHOOD MARKETS INC",
          "shares_traded": 49.0,
          "percent_of_etf": 0.0
        },
        {
          "direction": "Sell",
          "ticker": "PD",
          "company_name": "PAGERDUTY INC",
          "shares_traded": 9756.0,
          "percent_of_etf": 0.016
        },
        {
          "direction": "Sell",
          "ticker": "TWLO",
          "company_name": "TWILIO INC",
          "shares_traded": 21849.0,
          "percent_of_etf": 0.0994
        },
        {
          "direction": "Sell",
          "ticker": "PATH",
          "company_name": "UIPATH INC",
          "shares_traded": 105944.0,
          "percent_of_etf": 0.1459
        }
      ]
    },
    {
      "etf_ticker": "ARKG",
      "trade_date": "1/12/2024",
      "stocks": [
        {
          "direction": "Buy",
          "ticker": "TXG",
          "company_name": "10X GENOMICS INC",
          "shares_traded": 38042.0,
          "percent_of_etf": 0.0864
        },
        {
          "direction": "Buy",
          "ticker": "CRSP",
          "company_name": "CRISPR THERAPEUTICS AG",
          "shares_traded": 21197.0,
          "percent_of_etf": 0.0656
        },
        {
          "direction": "Buy",
          "ticker": "RXRX",
          "company_name": "RECURSION PHARMACEUTICALS",
          "shares_traded": 67422.0,
          "percent_of_etf": 0.0363
        },
        {
          "direction": "Buy",
          "ticker": "RPTX",
          "company_name": "REPARE THERAPEUTICS INC",
          "shares_traded": 15410.0,
          "percent_of_etf": 0.0049
        },
        {
          "direction": "Sell",
          "ticker": "EXAS",
          "company_name": "EXACT SCIENCES CORP",
          "shares_traded": 32057.0,
          "percent_of_etf": 0.1052
        }
      ]
    }
  ],
  "trade_notification_date": "1/12/2024",
  "sender_email_id": "ark@ark-funds.com",
  "email_date_time": "1/12/2024"
}

```

### For outlook message¶
In [ ]:
Copied!
```
output = program(email_msg_content=msg_content)

print("Output JSON from .msg file: ")
print(json.dumps(output.dict(), indent=2))

```

output = program(email_msg_content=msg_content) print("Output JSON from .msg file: ") print(json.dumps(output.dict(), indent=2))
```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
Function call: EmailData with args: {"etfs":[{"etf_ticker":"ARKK","trade_date":"1/12/2024","stocks":[{"direction":"Buy","ticker":"TSLA","company_name":"TESLA INC","shares_traded":93654,"percent_of_etf":0.2453},{"direction":"Buy","ticker":"TXG","company_name":"10X GENOMICS INC","shares_traded":159506,"percent_of_etf":0.0907},{"direction":"Buy","ticker":"CRSP","company_name":"CRISPR THERAPEUTICS AG","shares_traded":86268,"percent_of_etf":0.0669},{"direction":"Buy","ticker":"RXRX","company_name":"RECURSION PHARMACEUTICALS","shares_traded":289619,"percent_of_etf":0.0391},{"direction":"Sell","ticker":"HOOD","company_name":"ROBINHOOD MARKETS INC","shares_traded":927,"percent_of_etf":0.0001},{"direction":"Sell","ticker":"EXAS","company_name":"EXACT SCIENCES CORP","shares_traded":100766,"percent_of_etf":0.0829},{"direction":"Sell","ticker":"TWLO","company_name":"TWILIO INC","shares_traded":108523,"percent_of_etf":0.0957},{"direction":"Sell","ticker":"PD","company_name":"PAGERDUTY INC","shares_traded":302096,"percent_of_etf":0.0958},{"direction":"Sell","ticker":"PATH","company_name":"UIPATH INC","shares_traded":553172,"percent_of_etf":0.1476}]},{"etf_ticker":"ARKW","trade_date":"1/12/2024","stocks":[{"direction":"Buy","ticker":"TSLA","company_name":"TESLA INC","shares_traded":18148,"percent_of_etf":0.2454},{"direction":"Sell","ticker":"HOOD","company_name":"ROBINHOOD MARKETS INC","shares_traded":49,"percent_of_etf":0.0000},{"direction":"Sell","ticker":"PD","company_name":"PAGERDUTY INC","shares_traded":9756,"percent_of_etf":0.0160},{"direction":"Sell","ticker":"TWLO","company_name":"TWILIO INC","shares_traded":21849,"percent_of_etf":0.0994},{"direction":"Sell","ticker":"PATH","company_name":"UIPATH INC","shares_traded":105944,"percent_of_etf":0.1459}]},{"etf_ticker":"ARKG","trade_date":"1/12/2024","stocks":[{"direction":"Buy","ticker":"TXG","company_name":"10X GENOMICS INC","shares_traded":38042,"percent_of_etf":0.0864},{"direction":"Buy","ticker":"CRSP","company_name":"CRISPR THERAPEUTICS AG","shares_traded":21197,"percent_of_etf":0.0656},{"direction":"Buy","ticker":"RXRX","company_name":"RECURSION PHARMACEUTICALS","shares_traded":67422,"percent_of_etf":0.0363},{"direction":"Buy","ticker":"RPTX","company_name":"REPARE THERAPEUTICS INC","shares_traded":15410,"percent_of_etf":0.0049},{"direction":"Sell","ticker":"EXAS","company_name":"EXACT SCIENCES CORP","shares_traded":32057,"percent_of_etf":0.1052}]}],"trade_notification_date":"1/12/2024","sender_email_id":"ark-invest.com","email_date_time":"1/12/2024"}
Output JSON : 
{
  "etfs": [
    {
      "etf_ticker": "ARKK",
      "trade_date": "1/12/2024",
      "stocks": [
        {
          "direction": "Buy",
          "ticker": "TSLA",
          "company_name": "TESLA INC",
          "shares_traded": 93654.0,
          "percent_of_etf": 0.2453
        },
        {
          "direction": "Buy",
          "ticker": "TXG",
          "company_name": "10X GENOMICS INC",
          "shares_traded": 159506.0,
          "percent_of_etf": 0.0907
        },
        {
          "direction": "Buy",
          "ticker": "CRSP",
          "company_name": "CRISPR THERAPEUTICS AG",
          "shares_traded": 86268.0,
          "percent_of_etf": 0.0669
        },
        {
          "direction": "Buy",
          "ticker": "RXRX",
          "company_name": "RECURSION PHARMACEUTICALS",
          "shares_traded": 289619.0,
          "percent_of_etf": 0.0391
        },
        {
          "direction": "Sell",
          "ticker": "HOOD",
          "company_name": "ROBINHOOD MARKETS INC",
          "shares_traded": 927.0,
          "percent_of_etf": 0.0001
        },
        {
          "direction": "Sell",
          "ticker": "EXAS",
          "company_name": "EXACT SCIENCES CORP",
          "shares_traded": 100766.0,
          "percent_of_etf": 0.0829
        },
        {
          "direction": "Sell",
          "ticker": "TWLO",
          "company_name": "TWILIO INC",
          "shares_traded": 108523.0,
          "percent_of_etf": 0.0957
        },
        {
          "direction": "Sell",
          "ticker": "PD",
          "company_name": "PAGERDUTY INC",
          "shares_traded": 302096.0,
          "percent_of_etf": 0.0958
        },
        {
          "direction": "Sell",
          "ticker": "PATH",
          "company_name": "UIPATH INC",
          "shares_traded": 553172.0,
          "percent_of_etf": 0.1476
        }
      ]
    },
    {
      "etf_ticker": "ARKW",
      "trade_date": "1/12/2024",
      "stocks": [
        {
          "direction": "Buy",
          "ticker": "TSLA",
          "company_name": "TESLA INC",
          "shares_traded": 18148.0,
          "percent_of_etf": 0.2454
        },
        {
          "direction": "Sell",
          "ticker": "HOOD",
          "company_name": "ROBINHOOD MARKETS INC",
          "shares_traded": 49.0,
          "percent_of_etf": 0.0
        },
        {
          "direction": "Sell",
          "ticker": "PD",
          "company_name": "PAGERDUTY INC",
          "shares_traded": 9756.0,
          "percent_of_etf": 0.016
        },
        {
          "direction": "Sell",
          "ticker": "TWLO",
          "company_name": "TWILIO INC",
          "shares_traded": 21849.0,
          "percent_of_etf": 0.0994
        },
        {
          "direction": "Sell",
          "ticker": "PATH",
          "company_name": "UIPATH INC",
          "shares_traded": 105944.0,
          "percent_of_etf": 0.1459
        }
      ]
    },
    {
      "etf_ticker": "ARKG",
      "trade_date": "1/12/2024",
      "stocks": [
        {
          "direction": "Buy",
          "ticker": "TXG",
          "company_name": "10X GENOMICS INC",
          "shares_traded": 38042.0,
          "percent_of_etf": 0.0864
        },
        {
          "direction": "Buy",
          "ticker": "CRSP",
          "company_name": "CRISPR THERAPEUTICS AG",
          "shares_traded": 21197.0,
          "percent_of_etf": 0.0656
        },
        {
          "direction": "Buy",
          "ticker": "RXRX",
          "company_name": "RECURSION PHARMACEUTICALS",
          "shares_traded": 67422.0,
          "percent_of_etf": 0.0363
        },
        {
          "direction": "Buy",
          "ticker": "RPTX",
          "company_name": "REPARE THERAPEUTICS INC",
          "shares_traded": 15410.0,
          "percent_of_etf": 0.0049
        },
        {
          "direction": "Sell",
          "ticker": "EXAS",
          "company_name": "EXACT SCIENCES CORP",
          "shares_traded": 32057.0,
          "percent_of_etf": 0.1052
        }
      ]
    }
  ],
  "trade_notification_date": "1/12/2024",
  "sender_email_id": "ark-invest.com",
  "email_date_time": "1/12/2024"
}

```

