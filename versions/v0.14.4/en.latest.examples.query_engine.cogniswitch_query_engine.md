# Cogniswitch query engine
## CogniswitchQueryEngine¶
**Use CogniSwitch to build production ready applications that can consume, organize and retrieve knowledge flawlessly. Using the framework of your choice, in this case LlamaIndex, CogniSwitch helps alleviate the stress of decision making when it comes to choosing the right storage and retrieval formats. It also eradicates reliability issues and hallucinations when it comes to responses that are generated. Start interacting with your knowledge in 3 simple steps!**
Visit https://www.cogniswitch.ai/developer.  

**Registration:**
  * Signup with your email and verify your registration
  * You will get a mail with a platform token and oauth token for using the services.


**Upload Knowledge:**
  * There are two ways to add your knowledge into Cogniswitch.


  1. You can sign-in to Cogniswitch website and upload your document files or submit a url from the Document Upload page.  

  2. You can use the CogniswitchToolSpec in llama-hub tools to add document or a url in Cogniswitch.  



**CogniswitchQueryEngine:**  

  * Instantiate the cogniswitchQueryEngine with the tokens and API keys.
  * Use query_knowledge function in the Query Engine and input your query.   

  * You will get the answer from your knowledge as the response.   



### Import Required Libraries¶
In [ ]:
Copied!
```
import warnings

warnings.filterwarnings("ignore")
from llama_index.core.query_engine import CogniswitchQueryEngine

```

import warnings warnings.filterwarnings("ignore") from llama_index.core.query_engine import CogniswitchQueryEngine
### Cogniswitch Credentials and OpenAI token¶
In [ ]:
Copied!
```
# cs_token = <your cogniswitch platform token>
# OAI_token = <your openai token>
# oauth_token = <your cogniswitch apikey>

```

# cs_token =  # OAI_token =  # oauth_token = 
### Instantiate the Query Engine¶
In [ ]:
Copied!
```
query_engine = CogniswitchQueryEngine(
    cs_token=cs_token, OAI_token=OAI_token, apiKey=oauth_token
)

```

query_engine = CogniswitchQueryEngine( cs_token=cs_token, OAI_token=OAI_token, apiKey=oauth_token )
### Use the query_engine to chat with your knowledge¶
In [ ]:
Copied!
```
answer_response = query_engine.query_knowledge("tell me about cogniswitch")
print(answer_response)

```

answer_response = query_engine.query_knowledge("tell me about cogniswitch") print(answer_response)
```
CogniSwitch is a platform that offers a range of features to users. It helps users organize, explore, and manage data in an intuitive way. The platform visualizes complex ideas, simplifies them, and fine-tunes knowledge. Users can also consume knowledge on-demand through the CogniSwitch API. Furthermore, CogniSwitch provides data storage management capabilities.

```

