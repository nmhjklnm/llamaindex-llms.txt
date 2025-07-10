# Custom Planning Multi-Agent System¶
![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
In this notebook, we will explore how to prompt an LLM to write, refine, and follow a plan to generate a report using multiple agents.
This is not meant to be a comprehensive guide to creating a report generation system, but rather, giving you the knowledge and tools to build your own robust systems that can plan and orchestrate multiple agents to achieve a goal.
This notebook will assume that you have already either read the basic agent workflow notebook or the agent workflow documentation, as well as the workflow documentation.
## Setup¶
In this example, we will use `OpenAI` as our LLM. For all LLMs, check out the examples documentation or LlamaHub for a list of all supported LLMs and how to install/use them.
If we wanted, each agent could have a different LLM, but for this example, we will use the same LLM for all agents.
In [ ]:
Copied!
```
%pip install llama-index

```

%pip install llama-index
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI

sub_agent_llm = OpenAI(model="gpt-4.1-mini", api_key="sk-...")

```

from llama_index.llms.openai import OpenAI sub_agent_llm = OpenAI(model="gpt-4.1-mini", api_key="sk-...")
## System Design¶
Our system will have three agents:
  1. A `ResearchAgent` that will search the web for information on the given topic.
  2. A `WriteAgent` that will write the report using the information found by the `ResearchAgent`.
  3. A `ReviewAgent` that will review the report and provide feedback.


We will then use a top-level LLM to manually orchestrate and plan around the other agents to write our report.
While there are many ways to implement this system, in this case, we will use a single `web_search` tool to search the web for information on the given topic.
In [ ]:
Copied!
```
%pip install tavily-python

```

%pip install tavily-python
In [ ]:
Copied!
```
from tavily import AsyncTavilyClient


async def search_web(query: str) -> str:
    """Useful for using the web to answer questions."""
    client = AsyncTavilyClient(api_key="tvly-...")
    return str(await client.search(query))

```

from tavily import AsyncTavilyClient async def search_web(query: str) -> str: """Useful for using the web to answer questions.""" client = AsyncTavilyClient(api_key="tvly-...") return str(await client.search(query))
With our tool defined, we can now create our sub-agents.
If the LLM you are using supports tool calling, you can use the `FunctionAgent` class. Otherwise, you can use the `ReActAgent` class.
In [ ]:
Copied!
```
from llama_index.core.agent.workflow import FunctionAgent, ReActAgent

research_agent = FunctionAgent(
    name="ResearchAgent",
    description="Useful for recording research notes based on a specific prompt.",
    system_prompt=(
        "You are the ResearchAgent that can search the web for information on a given topic and record notes on the topic. "
        "You should output notes on the topic in a structured format."
    ),
    llm=sub_agent_llm,
    tools=[search_web],
)

write_agent = FunctionAgent(
    name="WriteAgent",
    description="Useful for writing a report based on the research notes or revising the report based on feedback.",
    system_prompt=(
        "You are the WriteAgent that can write a report on a given topic. "
        "Your report should be in a markdown format. The content should be grounded in the research notes. "
        "Return your markdown report surrounded by <report>...</report> tags."
    ),
    llm=sub_agent_llm,
    tools=[],
)

review_agent = FunctionAgent(
    name="ReviewAgent",
    description="Useful for reviewing a report and providing feedback.",
    system_prompt=(
        "You are the ReviewAgent that can review the write report and provide feedback. "
        "Your review should either approve the current report or request changes to be implemented."
    ),
    llm=sub_agent_llm,
    tools=[],
)

```

from llama_index.core.agent.workflow import FunctionAgent, ReActAgent research_agent = FunctionAgent( name="ResearchAgent", description="Useful for recording research notes based on a specific prompt.", system_prompt=( "You are the ResearchAgent that can search the web for information on a given topic and record notes on the topic. " "You should output notes on the topic in a structured format." ), llm=sub_agent_llm, tools=[search_web], ) write_agent = FunctionAgent( name="WriteAgent", description="Useful for writing a report based on the research notes or revising the report based on feedback.", system_prompt=( "You are the WriteAgent that can write a report on a given topic. " "Your report should be in a markdown format. The content should be grounded in the research notes. " "Return your markdown report surrounded by ... tags." ), llm=sub_agent_llm, tools=[], ) review_agent = FunctionAgent( name="ReviewAgent", description="Useful for reviewing a report and providing feedback.", system_prompt=( "You are the ReviewAgent that can review the write report and provide feedback. " "Your review should either approve the current report or request changes to be implemented." ), llm=sub_agent_llm, tools=[], )
With each agent defined, we can also write helper functions to help execute each agent.
In [ ]:
Copied!
```
import re
from llama_index.core.workflow import Context


async def call_research_agent(ctx: Context, prompt: str) -> str:
    """Useful for recording research notes based on a specific prompt."""
    result = await research_agent.run(
        user_msg=f"Write some notes about the following: {prompt}"
    )

    state = await ctx.store.get("state")
    state["research_notes"].append(str(result))
    await ctx.store.set("state", state)

    return str(result)


async def call_write_agent(ctx: Context) -> str:
    """Useful for writing a report based on the research notes or revising the report based on feedback."""
    state = await ctx.store.get("state")
    notes = state.get("research_notes", None)
    if not notes:
        return "No research notes to write from."

    user_msg = f"Write a markdown report from the following notes. Be sure to output the report in the following format: <report>...</report>:\n\n"

    # Add the feedback to the user message if it exists
    feedback = state.get("review", None)
    if feedback:
        user_msg += f"<feedback>{feedback}</feedback>\n\n"

    # Add the research notes to the user message
    notes = "\n\n".join(notes)
    user_msg += f"<research_notes>{notes}</research_notes>\n\n"

    # Run the write agent
    result = await write_agent.run(user_msg=user_msg)
    report = re.search(r"<report>(.*)</report>", str(result), re.DOTALL).group(
        1
    )
    state["report_content"] = str(report)
    await ctx.store.set("state", state)

    return str(report)


async def call_review_agent(ctx: Context) -> str:
    """Useful for reviewing the report and providing feedback."""
    state = await ctx.store.get("state")
    report = state.get("report_content", None)
    if not report:
        return "No report content to review."

    result = await review_agent.run(
        user_msg=f"Review the following report: {report}"
    )
    state["review"] = result
    await ctx.store.set("state", state)

    return result

```

import re from llama_index.core.workflow import Context async def call_research_agent(ctx: Context, prompt: str) -> str: """Useful for recording research notes based on a specific prompt.""" result = await research_agent.run( user_msg=f"Write some notes about the following: {prompt}" ) state = await ctx.store.get("state") state["research_notes"].append(str(result)) await ctx.store.set("state", state) return str(result) async def call_write_agent(ctx: Context) -> str: """Useful for writing a report based on the research notes or revising the report based on feedback.""" state = await ctx.store.get("state") notes = state.get("research_notes", None) if not notes: return "No research notes to write from." user_msg = f"Write a markdown report from the following notes. Be sure to output the report in the following format: ...:\n\n" # Add the feedback to the user message if it exists feedback = state.get("review", None) if feedback: user_msg += f"{feedback}\n\n" # Add the research notes to the user message notes = "\n\n".join(notes) user_msg += f"{notes}\n\n" # Run the write agent result = await write_agent.run(user_msg=user_msg) report = re.search(r"(.*)", str(result), re.DOTALL).group( 1 ) state["report_content"] = str(report) await ctx.store.set("state", state) return str(report) async def call_review_agent(ctx: Context) -> str: """Useful for reviewing the report and providing feedback.""" state = await ctx.store.get("state") report = state.get("report_content", None) if not report: return "No report content to review." result = await review_agent.run( user_msg=f"Review the following report: {report}" ) state["review"] = result await ctx.store.set("state", state) return result
## Defining the Planner Workflow¶
In order to plan around the other agents, we will write a custom workflow that will explicitly orchestrate and plan the other agents.
Here our prompt assumes a sequential plan, but we can expand it in the future to support parallel steps. (This just involves more complex parsing and prompting, which is left as an exercise for the reader.)
In [ ]:
Copied!
```
import re
import xml.etree.ElementTree as ET
from pydantic import BaseModel, Field
from typing import Any, Optional

from llama_index.core.llms import ChatMessage
from llama_index.core.workflow import (
    Context,
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)

PLANNER_PROMPT = """You are a planner chatbot. 

Given a user request and the current state, break the solution into ordered <step> blocks.  Each step must specify the agent to call and the message to send, e.g.
<plan>
  <step agent=\"ResearchAgent\">search for …</step>
  <step agent=\"WriteAgent\">draft a report …</step>
  ...
</plan>

<state>
{state}
</state>

<available_agents>
{available_agents}
</available_agents>

The general flow should be:
- Record research notes
- Write a report
- Review the report
- Write the report again if the review is not positive enough

If the user request does not require any steps, you can skip the <plan> block and respond directly.
"""


class InputEvent(StartEvent):
    user_msg: Optional[str] = Field(default=None)
    chat_history: list[ChatMessage]
    state: Optional[dict[str, Any]] = Field(default=None)


class OutputEvent(StopEvent):
    response: str
    chat_history: list[ChatMessage]
    state: dict[str, Any]


class StreamEvent(Event):
    delta: str


class PlanEvent(Event):
    step_info: str


# Modelling the plan
class PlanStep(BaseModel):
    agent_name: str
    agent_input: str


class Plan(BaseModel):
    steps: list[PlanStep]


class ExecuteEvent(Event):
    plan: Plan
    chat_history: list[ChatMessage]


class PlannerWorkflow(Workflow):
    llm: OpenAI = OpenAI(
        model="o3-mini",
        api_key="sk-...",
    )
    agents: dict[str, FunctionAgent] = {
        "ResearchAgent": research_agent,
        "WriteAgent": write_agent,
        "ReviewAgent": review_agent,
    }

    @step
    async def plan(
        self, ctx: Context, ev: InputEvent
    ) -> ExecuteEvent | OutputEvent:
        # Set initial state if it exists
        if ev.state:
            await ctx.store.set("state", ev.state)

        chat_history = ev.chat_history

        if ev.user_msg:
            user_msg = ChatMessage(
                role="user",
                content=ev.user_msg,
            )
            chat_history.append(user_msg)

        # Inject the system prompt with state and available agents
        state = await ctx.store.get("state")
        available_agents_str = "\n".join(
            [
                f'<agent name="{agent.name}">{agent.description}</agent>'
                for agent in self.agents.values()
            ]
        )
        system_prompt = ChatMessage(
            role="system",
            content=PLANNER_PROMPT.format(
                state=str(state),
                available_agents=available_agents_str,
            ),
        )

        # Stream the response from the llm
        response = await self.llm.astream_chat(
            messages=[system_prompt] + chat_history,
        )
        full_response = ""
        async for chunk in response:
            full_response += chunk.delta or ""
            if chunk.delta:
                ctx.write_event_to_stream(
                    StreamEvent(delta=chunk.delta),
                )

        # Parse the response into a plan and decide whether to execute or output
        xml_match = re.search(r"(<plan>.*</plan>)", full_response, re.DOTALL)

        if not xml_match:
            chat_history.append(
                ChatMessage(
                    role="assistant",
                    content=full_response,
                )
            )
            return OutputEvent(
                response=full_response,
                chat_history=chat_history,
                state=state,
            )
        else:
            xml_str = xml_match.group(1)
            root = ET.fromstring(xml_str)
            plan = Plan(steps=[])
            for step in root.findall("step"):
                plan.steps.append(
                    PlanStep(
                        agent_name=step.attrib["agent"],
                        agent_input=step.text.strip() if step.text else "",
                    )
                )

            return ExecuteEvent(plan=plan, chat_history=chat_history)

    @step
    async def execute(self, ctx: Context, ev: ExecuteEvent) -> InputEvent:
        chat_history = ev.chat_history
        plan = ev.plan

        for step in plan.steps:
            agent = self.agents[step.agent_name]
            agent_input = step.agent_input
            ctx.write_event_to_stream(
                PlanEvent(
                    step_info=f'<step agent="{step.agent_name}">{step.agent_input}</step>'
                ),
            )

            if step.agent_name == "ResearchAgent":
                await call_research_agent(ctx, agent_input)
            elif step.agent_name == "WriteAgent":
                # Note: we aren't passing the input from the plan since
                # we're using the state to drive the write agent
                await call_write_agent(ctx)
            elif step.agent_name == "ReviewAgent":
                await call_review_agent(ctx)

        state = await ctx.store.get("state")
        chat_history.append(
            ChatMessage(
                role="user",
                content=f"I've completed the previous steps, here's the updated state:\n\n<state>\n{state}\n</state>\n\nDo you need to continue and plan more steps?, If not, write a final response.",
            )
        )

        return InputEvent(
            chat_history=chat_history,
        )

```

import re import xml.etree.ElementTree as ET from pydantic import BaseModel, Field from typing import Any, Optional from llama_index.core.llms import ChatMessage from llama_index.core.workflow import ( Context, Event, StartEvent, StopEvent, Workflow, step, ) PLANNER_PROMPT = """You are a planner chatbot. Given a user request and the current state, break the solution into ordered  blocks. Each step must specify the agent to call and the message to send, e.g.  search for … draft a report … ...  {state}  {available_agents}  The general flow should be: - Record research notes - Write a report - Review the report - Write the report again if the review is not positive enough If the user request does not require any steps, you can skip the  block and respond directly. """ class InputEvent(StartEvent): user_msg: Optional[str] = Field(default=None) chat_history: list[ChatMessage] state: Optional[dict[str, Any]] = Field(default=None) class OutputEvent(StopEvent): response: str chat_history: list[ChatMessage] state: dict[str, Any] class StreamEvent(Event): delta: str class PlanEvent(Event): step_info: str # Modelling the plan class PlanStep(BaseModel): agent_name: str agent_input: str class Plan(BaseModel): steps: list[PlanStep] class ExecuteEvent(Event): plan: Plan chat_history: list[ChatMessage] class PlannerWorkflow(Workflow): llm: OpenAI = OpenAI( model="o3-mini", api_key="sk-...", ) agents: dict[str, FunctionAgent] = { "ResearchAgent": research_agent, "WriteAgent": write_agent, "ReviewAgent": review_agent, } @step async def plan( self, ctx: Context, ev: InputEvent ) -> ExecuteEvent | OutputEvent: # Set initial state if it exists if ev.state: await ctx.store.set("state", ev.state) chat_history = ev.chat_history if ev.user_msg: user_msg = ChatMessage( role="user", content=ev.user_msg, ) chat_history.append(user_msg) # Inject the system prompt with state and available agents state = await ctx.store.get("state") available_agents_str = "\n".join( [ f'{agent.description}' for agent in self.agents.values() ] ) system_prompt = ChatMessage( role="system", content=PLANNER_PROMPT.format( state=str(state), available_agents=available_agents_str, ), ) # Stream the response from the llm response = await self.llm.astream_chat( messages=[system_prompt] + chat_history, ) full_response = "" async for chunk in response: full_response += chunk.delta or "" if chunk.delta: ctx.write_event_to_stream( StreamEvent(delta=chunk.delta), ) # Parse the response into a plan and decide whether to execute or output xml_match = re.search(r"(.*)", full_response, re.DOTALL) if not xml_match: chat_history.append( ChatMessage( role="assistant", content=full_response, ) ) return OutputEvent( response=full_response, chat_history=chat_history, state=state, ) else: xml_str = xml_match.group(1) root = ET.fromstring(xml_str) plan = Plan(steps=[]) for step in root.findall("step"): plan.steps.append( PlanStep( agent_name=step.attrib["agent"], agent_input=step.text.strip() if step.text else "", ) ) return ExecuteEvent(plan=plan, chat_history=chat_history) @step async def execute(self, ctx: Context, ev: ExecuteEvent) -> InputEvent: chat_history = ev.chat_history plan = ev.plan for step in plan.steps: agent = self.agents[step.agent_name] agent_input = step.agent_input ctx.write_event_to_stream( PlanEvent( step_info=f'{step.agent_input}' ), ) if step.agent_name == "ResearchAgent": await call_research_agent(ctx, agent_input) elif step.agent_name == "WriteAgent": # Note: we aren't passing the input from the plan since # we're using the state to drive the write agent await call_write_agent(ctx) elif step.agent_name == "ReviewAgent": await call_review_agent(ctx) state = await ctx.store.get("state") chat_history.append( ChatMessage( role="user", content=f"I've completed the previous steps, here's the updated state:\n\n\n{state}\n\n\nDo you need to continue and plan more steps?, If not, write a final response.", ) ) return InputEvent( chat_history=chat_history, )
## Running the Workflow¶
With our custom planner defined, we can now run the workflow and see it in action!
As the workflow is running, we will stream the events to get an idea of what is happening under the hood.
In [ ]:
Copied!
```
planner_workflow = PlannerWorkflow(timeout=None)

handler = planner_workflow.run(
    user_msg=(
        "Write me a report on the history of the internet. "
        "Briefly describe the history of the internet, including the development of the internet, the development of the web, "
        "and the development of the internet in the 21st century."
    ),
    chat_history=[],
    state={
        "research_notes": [],
        "report_content": "Not written yet.",
        "review": "Review required.",
    },
)

current_agent = None
current_tool_calls = ""
async for event in handler.stream_events():
    if isinstance(event, PlanEvent):
        print("Executing plan step: ", event.step_info)
    elif isinstance(event, ExecuteEvent):
        print("Executing plan: ", event.plan)

result = await handler

```

planner_workflow = PlannerWorkflow(timeout=None) handler = planner_workflow.run( user_msg=( "Write me a report on the history of the internet. " "Briefly describe the history of the internet, including the development of the internet, the development of the web, " "and the development of the internet in the 21st century." ), chat_history=[], state={ "research_notes": [], "report_content": "Not written yet.", "review": "Review required.", }, ) current_agent = None current_tool_calls = "" async for event in handler.stream_events(): if isinstance(event, PlanEvent): print("Executing plan step: ", event.step_info) elif isinstance(event, ExecuteEvent): print("Executing plan: ", event.plan) result = await handler
```
Executing plan step:  <step agent="ResearchAgent">Record research notes on the history of the internet, detailing the development of the internet, the emergence and evolution of the web, and progress in the 21st century.</step>
Executing plan step:  <step agent="WriteAgent">Draft a report based on the recorded research notes about the history of the internet, including its early development, the creation and impact of the web, and milestones in the 21st century.</step>
Executing plan step:  <step agent="ReviewAgent">Review the generated report and provide feedback to ensure the report meets the request criteria.</step>
Executing plan step:  <step agent="WriteAgent">Revise the report by incorporating the review suggestions. Specifically, update Section 1 to clarify the role of the Internet Working Group (or IETF) and mention the transition to TCP/IP on January 1, 1983. In Section 2, include a note on the web as a system of interlinked hypertext documents, explain the Browser Wars with references to Netscape Navigator and Internet Explorer, and add that CSS was first proposed in 1996. In Section 3, briefly mention the transformative impact of mobile internet usage and smartphones, as well as outline emerging privacy and security challenges. Add a concluding section summarizing the overall impact of the internet and include references to authoritative sources where applicable.</step>

```

In [ ]:
Copied!
```
print(result.response)

```

print(result.response)
```
Final Response: 

No further planning steps are needed. The report on the History of the Internet has been completed and reviewed, with clear suggestions provided for minor enhancements. You can now incorporate those recommendations into your final report if desired.

```

Now, we can retrieve the final report in the system for ourselves.
In [ ]:
Copied!
```
state = await handler.ctx.get("state")
print(state["report_content"])

```

state = await handler.ctx.get("state") print(state["report_content"])
```
# History of the Internet

## 1. Development of the Internet

The internet's origins trace back to **ARPANET**, developed in 1969 by the U.S. Defense Department's Advanced Research Projects Agency (DARPA) as a military defense communication system during the Cold War. ARPANET initially connected research programs across universities and government institutions, laying the groundwork for packet-switching networks.

In the late 1970s, as ARPANET expanded, coordination bodies such as the **International Cooperation Board** and the **Internet Configuration Control Board** were established to manage the growing research community and oversee internet development. The **Internet Working Group (IWG)**, which later evolved into the **Internet Engineering Task Force (IETF)**, played a crucial role in developing protocols and standards.

A pivotal milestone occurred on **January 1, 1983**, when ARPANET adopted the **Transmission Control Protocol/Internet Protocol (TCP/IP)** suite, marking the transition from ARPANET to the modern internet. This standardization enabled diverse networks to interconnect seamlessly.

During the 1970s and 1980s, **commercial packet networks** such as Telenet and Tymnet emerged, providing broader access to remote computers and facilitating early commercial use of network services. The **National Science Foundation (NSF)** further expanded internet access to the scientific and academic communities through NSFNET, which became a backbone connecting regional networks.

By the late 1980s and early 1990s, commercial internet backbones connected through **Network Access Points (NAPs)**, enabling widespread internet connectivity beyond academia and government, setting the stage for the internet's global expansion.

## 2. Emergence and Evolution of the Web

The **World Wide Web** was invented in 1989 by **Tim Berners-Lee** while working at CERN. The web introduced a system of interlinked hypertext documents accessed via the internet, revolutionizing information sharing.

By December 1990, Berners-Lee developed the foundational technologies of the web: **HTTP (HyperText Transfer Protocol)**, **HTML (HyperText Markup Language)**, the first web browser/editor, the first web server, and the first website. The web became publicly accessible outside CERN by 1991, rapidly gaining popularity.

In 1994, Berners-Lee founded the **World Wide Web Consortium (W3C)** at MIT to develop open standards ensuring the web's interoperability and growth.

The mid-1990s saw significant technological advancements:

- **JavaScript** was introduced in 1995, enabling dynamic and interactive web content.
- **Cascading Style Sheets (CSS)** were first proposed in **1996**, allowing separation of content from presentation and enhancing web design flexibility.

During this period, the **"Browser Wars"**—a competition primarily between **Netscape Navigator** and **Microsoft Internet Explorer**—spurred rapid innovation and adoption of web technologies, shaping the modern browsing experience.

## 3. Progress in the 21st Century

The 21st century witnessed transformative growth in internet technology and usage:

- The rise of **broadband**, **fiber-optic networks**, and **5G** technology provided high-speed, reliable connectivity worldwide.
- The proliferation of **smartphones** and **mobile internet usage** fundamentally changed how people accessed and interacted with the internet.
- **Social media platforms** emerged, revolutionizing communication, social interaction, and information dissemination.
- **Cloud computing** transformed data storage and processing by enabling remote access to powerful servers.
- The **Internet of Things (IoT)** connected everyday devices to the internet, integrating digital connectivity into physical environments.
- Advances in **artificial intelligence**, **blockchain**, and **sensor networks** further expanded internet capabilities and applications.

Alongside these advances, privacy and security challenges have become increasingly prominent, prompting ongoing efforts to protect users and data in an interconnected world.

## Conclusion

From its origins as a military research project to a global network connecting billions, the internet has profoundly transformed society. The invention of the World Wide Web made information universally accessible, while continuous technological innovations have reshaped communication, commerce, education, and entertainment. As the internet continues to evolve, addressing challenges such as privacy and security remains essential to harnessing its full potential for future generations.

---

### References

- Leiner, B. M., Cerf, V. G., Clark, D. D., et al. (1997). A Brief History of the Internet. *ACM SIGCOMM Computer Communication Review*, 39(5), 22–31.
- Berners-Lee, T., & Fischetti, M. (1999). *Weaving the Web: The Original Design and Ultimate Destiny of the World Wide Web*. Harper.
- World Wide Web Consortium (W3C). (n.d.). About W3C. https://www.w3.org/Consortium/
- Abbate, J. (1999). *Inventing the Internet*. MIT Press.
- Internet Society. (n.d.). A Short History of the Internet. https://www.internetsociety.org/internet/history-internet/brief-history-internet/


```

In [ ]:
Copied!
```
print(state["review"])

```

print(state["review"])
```
The report on the History of the Internet is well-structured, clear, and covers the major milestones and developments comprehensively. It effectively divides the content into logical sections: the development of the internet, the emergence and evolution of the web, and progress in the 21st century. The information is accurate and presented in a concise manner.

However, I have a few suggestions to improve clarity and completeness:

1. **Section 1 - Development of the Internet:**
   - The term "Internet Working Group" is mentioned but could be clarified as the "Internet Working Group (IWG)" or "Internet Engineering Task Force (IETF)" to avoid confusion.
   - It might be helpful to briefly mention the transition from ARPANET to the modern internet, including the adoption of TCP/IP on January 1, 1983, which is a key milestone.
   - The role of commercial packet networks could be expanded slightly to mention specific examples or their impact.

2. **Section 2 - Emergence and Evolution of the Web:**
   - The report correctly credits Tim Berners-Lee but could mention the significance of the web being a system of interlinked hypertext documents accessed via the internet.
   - The "Browser Wars" could be briefly explained, naming key browsers involved (e.g., Netscape Navigator and Internet Explorer) to provide context.
   - The introduction of CSS could include the year it was first proposed (1996) for completeness.

3. **Section 3 - Progress in the 21st Century:**
   - The report covers major technological advances well but could briefly mention the rise of mobile internet usage and smartphones as a transformative factor.
   - It might be beneficial to note privacy and security challenges that have emerged alongside technological progress.

4. **General:**
   - Adding references or citations to authoritative sources would strengthen the report's credibility.
   - Including a brief conclusion summarizing the internet's impact on society could provide a strong closing.

Overall, the report is informative and well-written but would benefit from these enhancements to improve depth and clarity.

**Recommendation:** Please implement the suggested changes to enhance the report before approval.

```

