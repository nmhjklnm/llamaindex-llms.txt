## ¶
# Creating a CodeAct Agent From Scratch¶
While LlamaIndex provides a pre-built CodeActAgent, we can also create our own from scratch.
This way, we can fully understand and customize the agent's behaviour beyond what is provided by the pre-built agent.
In this notebook, we will
  1. Create a workflow for generating and parsing code
  2. Implement basic code execution
  3. Add memory and state to the agent


## Setting up Functions for our Agent¶
If we want our agent to execute our code, we need to deine the code for it to execute!
For now, let's use a few basic math functions.
In [ ]:
Copied!
```
# Define a few helper functions
def add(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b


def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b


def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b


def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    return a / b

```

# Define a few helper functions def add(a: int, b: int) -> int: """Add two numbers together""" return a + b def subtract(a: int, b: int) -> int: """Subtract two numbers""" return a - b def multiply(a: int, b: int) -> int: """Multiply two numbers""" return a * b def divide(a: int, b: int) -> float: """Divide two numbers""" return a / b
## Creating a Code Executor¶
In order to execute code, we need to create a code executor.
Here, we will use a simple in-process code executor that maintains it's own state.
**NOTE:** This is a simple example, and does not include proper sandboxing. In a production environment, you should use tools like docker or proper code sandboxing environments.
In [ ]:
Copied!
```
from typing import Any, Dict, Tuple
import io
import contextlib
import ast
import traceback


class SimpleCodeExecutor:
    """
    A simple code executor that runs Python code with state persistence.

    This executor maintains a global and local state between executions,
    allowing for variables to persist across multiple code runs.

    NOTE: not safe for production use! Use with caution.
    """

    def __init__(self, locals: Dict[str, Any], globals: Dict[str, Any]):
        """
        Initialize the code executor.

        Args:
            locals: Local variables to use in the execution context
            globals: Global variables to use in the execution context
        """
        # State that persists between executions
        self.globals = globals
        self.locals = locals

    def execute(self, code: str) -> Tuple[bool, str, Any]:
        """
        Execute Python code and capture output and return values.

        Args:
            code: Python code to execute

        Returns:
            Dict with keys `success`, `output`, and `return_value`
        """
        # Capture stdout and stderr
        stdout = io.StringIO()
        stderr = io.StringIO()

        output = ""
        return_value = None
        try:
            # Execute with captured output
            with contextlib.redirect_stdout(
                stdout
            ), contextlib.redirect_stderr(stderr):
                # Try to detect if there's a return value (last expression)
                try:
                    tree = ast.parse(code)
                    last_node = tree.body[-1] if tree.body else None

                    # If the last statement is an expression, capture its value
                    if isinstance(last_node, ast.Expr):
                        # Split code to add a return value assignment
                        last_line = code.rstrip().split("\n")[-1]
                        exec_code = (
                            code[: -len(last_line)]
                            + "\n__result__ = "
                            + last_line
                        )

                        # Execute modified code
                        exec(exec_code, self.globals, self.locals)
                        return_value = self.locals.get("__result__")
                    else:
                        # Normal execution
                        exec(code, self.globals, self.locals)
                except:
                    # If parsing fails, just execute the code as is
                    exec(code, self.globals, self.locals)

            # Get output
            output = stdout.getvalue()
            if stderr.getvalue():
                output += "\n" + stderr.getvalue()

        except Exception as e:
            # Capture exception information
            output = f"Error: {type(e).__name__}: {str(e)}\n"
            output += traceback.format_exc()

        if return_value is not None:
            output += "\n\n" + str(return_value)

        return output

```

from typing import Any, Dict, Tuple import io import contextlib import ast import traceback class SimpleCodeExecutor: """ A simple code executor that runs Python code with state persistence. This executor maintains a global and local state between executions, allowing for variables to persist across multiple code runs. NOTE: not safe for production use! Use with caution. """ def __init__(self, locals: Dict[str, Any], globals: Dict[str, Any]): """ Initialize the code executor. Args: locals: Local variables to use in the execution context globals: Global variables to use in the execution context """ # State that persists between executions self.globals = globals self.locals = locals def execute(self, code: str) -> Tuple[bool, str, Any]: """ Execute Python code and capture output and return values. Args: code: Python code to execute Returns: Dict with keys `success`, `output`, and `return_value` """ # Capture stdout and stderr stdout = io.StringIO() stderr = io.StringIO() output = "" return_value = None try: # Execute with captured output with contextlib.redirect_stdout( stdout ), contextlib.redirect_stderr(stderr): # Try to detect if there's a return value (last expression) try: tree = ast.parse(code) last_node = tree.body[-1] if tree.body else None # If the last statement is an expression, capture its value if isinstance(last_node, ast.Expr): # Split code to add a return value assignment last_line = code.rstrip().split("\n")[-1] exec_code = ( code[: -len(last_line)] + "\n__result__ = " + last_line ) # Execute modified code exec(exec_code, self.globals, self.locals) return_value = self.locals.get("__result__") else: # Normal execution exec(code, self.globals, self.locals) except: # If parsing fails, just execute the code as is exec(code, self.globals, self.locals) # Get output output = stdout.getvalue() if stderr.getvalue(): output += "\n" + stderr.getvalue() except Exception as e: # Capture exception information output = f"Error: {type(e).__name__}: {str(e)}\n" output += traceback.format_exc() if return_value is not None: output += "\n\n" + str(return_value) return output
In [ ]:
Copied!
```
code_executor = SimpleCodeExecutor(
    # give access to our functions defined above
    locals={
        "add": add,
        "subtract": subtract,
        "multiply": multiply,
        "divide": divide,
    },
    globals={
        # give access to all builtins
        "__builtins__": __builtins__,
        # give access to numpy
        "np": __import__("numpy"),
    },
)

```

code_executor = SimpleCodeExecutor( # give access to our functions defined above locals={ "add": add, "subtract": subtract, "multiply": multiply, "divide": divide, }, globals={ # give access to all builtins "__builtins__": __builtins__, # give access to numpy "np": __import__("numpy"), }, )
## Defining the CodeAct Agent¶
Now, we can using LlamaIndex Workflows to define the workflow for our agent.
The basic flow is:
  * take in our prompt + chat history
  * parse out the code to execute (if any)
  * execute the code
  * provide the output of the code execution back to the agent
  * repeat until the agent is satisfied with the answer


First, we can create the events in the workflow.
In [ ]:
Copied!
```
from llama_index.core.llms import ChatMessage
from llama_index.core.workflow import Event


class InputEvent(Event):
    input: list[ChatMessage]


class StreamEvent(Event):
    delta: str


class CodeExecutionEvent(Event):
    code: str

```

from llama_index.core.llms import ChatMessage from llama_index.core.workflow import Event class InputEvent(Event): input: list[ChatMessage] class StreamEvent(Event): delta: str class CodeExecutionEvent(Event): code: str
Next, we can define the workflow that orchestrates using these events.
In [ ]:
Copied!
```
import inspect
import re
from typing import Any, Callable, List

from llama_index.core.llms import ChatMessage, LLM
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools.types import BaseTool
from llama_index.core.workflow import (
    Context,
    Workflow,
    StartEvent,
    StopEvent,
    step,
)
from llama_index.llms.openai import OpenAI


CODEACT_SYSTEM_PROMPT = """
You are a helpful assistant that can execute code.

Given the chat history, you can write code within <execute>...</execute> tags to help the user with their question.

In your code, you can reference any previously used variables or functions.

The user has also provided you with some predefined functions:
{fn_str}

To execute code, write the code between <execute>...</execute> tags.
"""


class CodeActAgent(Workflow):
    def __init__(
        self,
        fns: List[Callable],
        code_execute_fn: Callable,
        llm: LLM | None = None,
        **workflow_kwargs: Any,
    ) -> None:
        super().__init__(**workflow_kwargs)
        self.fns = fns or []
        self.code_execute_fn = code_execute_fn
        self.llm = llm or OpenAI(model="gpt-4o-mini")

        # parse the functions into truncated function strings
        self.fn_str = "\n\n".join(
            f'def {fn.__name__}{str(inspect.signature(fn))}:\n    """ {fn.__doc__} """\n    ...'
            for fn in self.fns
        )
        self.system_message = ChatMessage(
            role="system",
            content=CODEACT_SYSTEM_PROMPT.format(fn_str=self.fn_str),
        )

    def _parse_code(self, response: str) -> str | None:
        # find the code between <execute>...</execute> tags
        matches = re.findall(r"<execute>(.*?)</execute>", response, re.DOTALL)
        if matches:
            return "\n\n".join(matches)

        return None

    @step
    async def prepare_chat_history(
        self, ctx: Context, ev: StartEvent
    ) -> InputEvent:
        # check if memory is setup
        memory = await ctx.get("memory", default=None)
        if not memory:
            memory = ChatMemoryBuffer.from_defaults(llm=self.llm)

        # get user input
        user_input = ev.get("user_input")
        if user_input is None:
            raise ValueError("user_input kwarg is required")
        user_msg = ChatMessage(role="user", content=user_input)
        memory.put(user_msg)

        # get chat history
        chat_history = memory.get()

        # update context
        await ctx.set("memory", memory)

        # add the system message to the chat history and return
        return InputEvent(input=[self.system_message, *chat_history])

    @step
    async def handle_llm_input(
        self, ctx: Context, ev: InputEvent
    ) -> CodeExecutionEvent | StopEvent:
        chat_history = ev.input

        # stream the response
        response_stream = await self.llm.astream_chat(chat_history)
        async for response in response_stream:
            ctx.write_event_to_stream(StreamEvent(delta=response.delta or ""))

        # save the final response, which should have all content
        memory = await ctx.get("memory")
        memory.put(response.message)
        await ctx.set("memory", memory)

        # get the code to execute
        code = self._parse_code(response.message.content)

        if not code:
            return StopEvent(result=response)
        else:
            return CodeExecutionEvent(code=code)

    @step
    async def handle_code_execution(
        self, ctx: Context, ev: CodeExecutionEvent
    ) -> InputEvent:
        # execute the code
        ctx.write_event_to_stream(ev)
        output = self.code_execute_fn(ev.code)

        # update the memory
        memory = await ctx.get("memory")
        memory.put(ChatMessage(role="assistant", content=output))
        await ctx.set("memory", memory)

        # get the latest chat history and loop back to the start
        chat_history = memory.get()
        return InputEvent(input=[self.system_message, *chat_history])

```

import inspect import re from typing import Any, Callable, List from llama_index.core.llms import ChatMessage, LLM from llama_index.core.memory import ChatMemoryBuffer from llama_index.core.tools.types import BaseTool from llama_index.core.workflow import ( Context, Workflow, StartEvent, StopEvent, step, ) from llama_index.llms.openai import OpenAI CODEACT_SYSTEM_PROMPT = """ You are a helpful assistant that can execute code. Given the chat history, you can write code within ... tags to help the user with their question. In your code, you can reference any previously used variables or functions. The user has also provided you with some predefined functions: {fn_str} To execute code, write the code between ... tags. """ class CodeActAgent(Workflow): def __init__( self, fns: List[Callable], code_execute_fn: Callable, llm: LLM | None = None, **workflow_kwargs: Any, ) -> None: super().__init__(**workflow_kwargs) self.fns = fns or [] self.code_execute_fn = code_execute_fn self.llm = llm or OpenAI(model="gpt-4o-mini") # parse the functions into truncated function strings self.fn_str = "\n\n".join( f'def {fn.__name__}{str(inspect.signature(fn))}:\n """ {fn.__doc__} """\n ...' for fn in self.fns ) self.system_message = ChatMessage( role="system", content=CODEACT_SYSTEM_PROMPT.format(fn_str=self.fn_str), ) def _parse_code(self, response: str) -> str | None: # find the code between ... tags matches = re.findall(r"(.*?)", response, re.DOTALL) if matches: return "\n\n".join(matches) return None @step async def prepare_chat_history( self, ctx: Context, ev: StartEvent ) -> InputEvent: # check if memory is setup memory = await ctx.get("memory", default=None) if not memory: memory = ChatMemoryBuffer.from_defaults(llm=self.llm) # get user input user_input = ev.get("user_input") if user_input is None: raise ValueError("user_input kwarg is required") user_msg = ChatMessage(role="user", content=user_input) memory.put(user_msg) # get chat history chat_history = memory.get() # update context await ctx.set("memory", memory) # add the system message to the chat history and return return InputEvent(input=[self.system_message, *chat_history]) @step async def handle_llm_input( self, ctx: Context, ev: InputEvent ) -> CodeExecutionEvent | StopEvent: chat_history = ev.input # stream the response response_stream = await self.llm.astream_chat(chat_history) async for response in response_stream: ctx.write_event_to_stream(StreamEvent(delta=response.delta or "")) # save the final response, which should have all content memory = await ctx.get("memory") memory.put(response.message) await ctx.set("memory", memory) # get the code to execute code = self._parse_code(response.message.content) if not code: return StopEvent(result=response) else: return CodeExecutionEvent(code=code) @step async def handle_code_execution( self, ctx: Context, ev: CodeExecutionEvent ) -> InputEvent: # execute the code ctx.write_event_to_stream(ev) output = self.code_execute_fn(ev.code) # update the memory memory = await ctx.get("memory") memory.put(ChatMessage(role="assistant", content=output)) await ctx.set("memory", memory) # get the latest chat history and loop back to the start chat_history = memory.get() return InputEvent(input=[self.system_message, *chat_history])
## Testing the CodeAct Agent¶
Now, we can test out the CodeAct Agent!
We'll create a simple agent and slowly build up the complexity with requests.
In [ ]:
Copied!
```
from llama_index.core.workflow import Context

agent = CodeActAgent(
    fns=[add, subtract, multiply, divide],
    code_execute_fn=code_executor.execute,
    llm=OpenAI(model="gpt-4o-mini", api_key="sk-..."),
)

# context to hold the agent's state / memory
ctx = Context(agent)

```

from llama_index.core.workflow import Context agent = CodeActAgent( fns=[add, subtract, multiply, divide], code_execute_fn=code_executor.execute, llm=OpenAI(model="gpt-4o-mini", api_key="sk-..."), ) # context to hold the agent's state / memory ctx = Context(agent)
In [ ]:
Copied!
```
async def run_agent_verbose(agent: CodeActAgent, ctx: Context, query: str):
    handler = agent.run(user_input=query, ctx=ctx)
    print(f"User:  {query}")
    async for event in handler.stream_events():
        if isinstance(event, StreamEvent):
            print(f"{event.delta}", end="", flush=True)
        elif isinstance(event, CodeExecutionEvent):
            print(f"\n-----------\nParsed code:\n{event.code}\n")

    return await handler

```

async def run_agent_verbose(agent: CodeActAgent, ctx: Context, query: str): handler = agent.run(user_input=query, ctx=ctx) print(f"User: {query}") async for event in handler.stream_events(): if isinstance(event, StreamEvent): print(f"{event.delta}", end="", flush=True) elif isinstance(event, CodeExecutionEvent): print(f"\n-----------\nParsed code:\n{event.code}\n") return await handler
In [ ]:
Copied!
```
response = await run_agent_verbose(
    agent, ctx, "Calculate the sum of all numbers from 1 to 10"
)

```

response = await run_agent_verbose( agent, ctx, "Calculate the sum of all numbers from 1 to 10" )
```
User:  Calculate the sum of all numbers from 1 to 10
To calculate the sum of all numbers from 1 to 10, we can use the `add` function in a loop. Here's how we can do it:

<execute>
total_sum = 0
for number in range(1, 11):
    total_sum = add(total_sum, number)
total_sum
</execute>
-----------
Parsed code:

total_sum = 0
for number in range(1, 11):
    total_sum = add(total_sum, number)
total_sum


The sum of all numbers from 1 to 10 is 55.
```

In [ ]:
Copied!
```
response = await run_agent_verbose(
    agent, ctx, "Add 5 and 3, then multiply the result by 2"
)

```

response = await run_agent_verbose( agent, ctx, "Add 5 and 3, then multiply the result by 2" )
```
User:  Add 5 and 3, then multiply the result by 2
To perform the calculation, we will first add 5 and 3 using the `add` function, and then multiply the result by 2 using the `multiply` function. Here's how we can do it:

<execute>
result_addition = add(5, 3)
final_result = multiply(result_addition, 2)
final_result
</execute>
-----------
Parsed code:

result_addition = add(5, 3)
final_result = multiply(result_addition, 2)
final_result


The final result of adding 5 and 3, then multiplying by 2, is 16.
```

In [ ]:
Copied!
```
response = await run_agent_verbose(
    agent, ctx, "Calculate the sum of the first 10 fibonacci numbers0"
)

```

response = await run_agent_verbose( agent, ctx, "Calculate the sum of the first 10 fibonacci numbers0" )
```
User:  Calculate the sum of the first 10 fibonacci numbers0
To calculate the sum of the first 10 Fibonacci numbers, we first need to generate the Fibonacci sequence up to the 10th number and then sum those numbers. The Fibonacci sequence starts with 0 and 1, and each subsequent number is the sum of the two preceding ones.

Here's how we can do it:

<execute>
def fibonacci(n: int) -> int:
    """ Return the nth Fibonacci number """
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

# Calculate the sum of the first 10 Fibonacci numbers
fibonacci_sum = 0
for i in range(10):
    fibonacci_sum = add(fibonacci_sum, fibonacci(i))

fibonacci_sum
</execute>
-----------
Parsed code:

def fibonacci(n: int) -> int:
    """ Return the nth Fibonacci number """
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

# Calculate the sum of the first 10 Fibonacci numbers
fibonacci_sum = 0
for i in range(10):
    fibonacci_sum = add(fibonacci_sum, fibonacci(i))

fibonacci_sum


The sum of the first 10 Fibonacci numbers is 55.
```

In [ ]:
Copied!
```
response = await run_agent_verbose(
    agent, ctx, "Calculate the sum of the first 20 fibonacci numbers"
)

```

response = await run_agent_verbose( agent, ctx, "Calculate the sum of the first 20 fibonacci numbers" )
```
User:  Calculate the sum of the first 20 fibonacci numbers
To calculate the sum of the first 20 Fibonacci numbers, we can use the same approach as before, but this time we will iterate up to 20. Here's how we can do it:

<execute>
# Calculate the sum of the first 20 Fibonacci numbers
fibonacci_sum_20 = 0
for i in range(20):
    fibonacci_sum_20 = add(fibonacci_sum_20, fibonacci(i))

fibonacci_sum_20
</execute>
-----------
Parsed code:

# Calculate the sum of the first 20 Fibonacci numbers
fibonacci_sum_20 = 0
for i in range(20):
    fibonacci_sum_20 = add(fibonacci_sum_20, fibonacci(i))

fibonacci_sum_20


The sum of the first 20 Fibonacci numbers is 6765.
```

