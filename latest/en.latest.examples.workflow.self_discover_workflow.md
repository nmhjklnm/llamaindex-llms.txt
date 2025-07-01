# Self-Discover Workflow¶
This notebooks shows how to implement SELF-DISCOVER.
It has two stages for the given task:
  1. STAGE-1:
a. SELECT: Selects subset of reasoning Modules.
b. ADAPT: Adapts selected reasoning modules to the task.
c. IMPLEMENT: It gives reasoning structure for the task.
  2. STAGE-2: Uses the generated reasoning structure for the task to generate an answer.


The implementation is inspired from the codebase
In [ ]:
Copied!
```
%pip install -U llama-index

```

%pip install -U llama-index
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "<Your OpenAI API Key>"

```

import os os.environ["OPENAI_API_KEY"] = ""
Since workflows are async first, this all runs fine in a notebook. If you were running in your own code, you would want to use `asyncio.run()` to start an async event loop if one isn't already running.
```
async def main():
    <async code>

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

```

## Setup¶
Set up the reasoning modules and the prompt templates.
In [ ]:
Copied!
```
from llama_index.core.prompts import PromptTemplate

_REASONING_MODULES = [
    "1. How could I devise an experiment to help solve that problem?",
    "2. Make a list of ideas for solving this problem, and apply them one by one to the problem to see if any progress can be made.",
    "3. How could I measure progress on this problem?",
    "4. How can I simplify the problem so that it is easier to solve?",
    "5. What are the key assumptions underlying this problem?",
    "6. What are the potential risks and drawbacks of each solution?",
    "7. What are the alternative perspectives or viewpoints on this problem?",
    "8. What are the long-term implications of this problem and its solutions?",
    "9. How can I break down this problem into smaller, more manageable parts?",
    "10. Critical Thinking: This style involves analyzing the problem from different perspectives, questioning assumptions, and evaluating the evidence or information available. It focuses on logical reasoning, evidence-based decision-making, and identifying potential biases or flaws in thinking.",
    "11. Try creative thinking, generate innovative and out-of-the-box ideas to solve the problem. Explore unconventional solutions, thinking beyond traditional boundaries, and encouraging imagination and originality.",
    "12. Seek input and collaboration from others to solve the problem. Emphasize teamwork, open communication, and leveraging the diverse perspectives and expertise of a group to come up with effective solutions.",
    "13. Use systems thinking: Consider the problem as part of a larger system and understanding the interconnectedness of various elements. Focuses on identifying the underlying causes, feedback loops, and interdependencies that influence the problem, and developing holistic solutions that address the system as a whole.",
    "14. Use Risk Analysis: Evaluate potential risks, uncertainties, and tradeoffs associated with different solutions or approaches to a problem. Emphasize assessing the potential consequences and likelihood of success or failure, and making informed decisions based on a balanced analysis of risks and benefits.",
    "15. Use Reflective Thinking: Step back from the problem, take the time for introspection and self-reflection. Examine personal biases, assumptions, and mental models that may influence problem-solving, and being open to learning from past experiences to improve future approaches.",
    "16. What is the core issue or problem that needs to be addressed?",
    "17. What are the underlying causes or factors contributing to the problem?",
    "18. Are there any potential solutions or strategies that have been tried before? If yes, what were the outcomes and lessons learned?",
    "19. What are the potential obstacles or challenges that might arise in solving this problem?",
    "20. Are there any relevant data or information that can provide insights into the problem? If yes, what data sources are available, and how can they be analyzed?",
    "21. Are there any stakeholders or individuals who are directly affected by the problem? What are their perspectives and needs?",
    "22. What resources (financial, human, technological, etc.) are needed to tackle the problem effectively?",
    "23. How can progress or success in solving the problem be measured or evaluated?",
    "24. What indicators or metrics can be used?",
    "25. Is the problem a technical or practical one that requires a specific expertise or skill set? Or is it more of a conceptual or theoretical problem?",
    "26. Does the problem involve a physical constraint, such as limited resources, infrastructure, or space?",
    "27. Is the problem related to human behavior, such as a social, cultural, or psychological issue?",
    "28. Does the problem involve decision-making or planning, where choices need to be made under uncertainty or with competing objectives?",
    "29. Is the problem an analytical one that requires data analysis, modeling, or optimization techniques?",
    "30. Is the problem a design challenge that requires creative solutions and innovation?",
    "31. Does the problem require addressing systemic or structural issues rather than just individual instances?",
    "32. Is the problem time-sensitive or urgent, requiring immediate attention and action?",
    "33. What kinds of solution typically are produced for this kind of problem specification?",
    "34. Given the problem specification and the current best solution, have a guess about other possible solutions."
    "35. Let’s imagine the current best solution is totally wrong, what other ways are there to think about the problem specification?"
    "36. What is the best way to modify this current best solution, given what you know about these kinds of problem specification?"
    "37. Ignoring the current best solution, create an entirely new solution to the problem."
    "38. Let’s think step by step ."
    "39. Let’s make a step by step plan and implement it with good notation and explanation.",
]

_REASONING_MODULES = "\n".join(_REASONING_MODULES)

SELECT_PRMOPT_TEMPLATE = PromptTemplate(
    "Given the task: {task}, which of the following reasoning modules are relevant? Do not elaborate on why.\n\n {reasoning_modules}"
)

ADAPT_PROMPT_TEMPLATE = PromptTemplate(
    "Without working out the full solution, adapt the following reasoning modules to be specific to our task:\n{selected_modules}\n\nOur task:\n{task}"
)

IMPLEMENT_PROMPT_TEMPLATE = PromptTemplate(
    "Without working out the full solution, create an actionable reasoning structure for the task using these adapted reasoning modules:\n{adapted_modules}\n\nTask Description:\n{task}"
)

REASONING_PROMPT_TEMPLATE = PromptTemplate(
    "Using the following reasoning structure: {reasoning_structure}\n\nSolve this task, providing your final answer: {task}"
)

```

from llama_index.core.prompts import PromptTemplate _REASONING_MODULES = [ "1. How could I devise an experiment to help solve that problem?", "2. Make a list of ideas for solving this problem, and apply them one by one to the problem to see if any progress can be made.", "3. How could I measure progress on this problem?", "4. How can I simplify the problem so that it is easier to solve?", "5. What are the key assumptions underlying this problem?", "6. What are the potential risks and drawbacks of each solution?", "7. What are the alternative perspectives or viewpoints on this problem?", "8. What are the long-term implications of this problem and its solutions?", "9. How can I break down this problem into smaller, more manageable parts?", "10. Critical Thinking: This style involves analyzing the problem from different perspectives, questioning assumptions, and evaluating the evidence or information available. It focuses on logical reasoning, evidence-based decision-making, and identifying potential biases or flaws in thinking.", "11. Try creative thinking, generate innovative and out-of-the-box ideas to solve the problem. Explore unconventional solutions, thinking beyond traditional boundaries, and encouraging imagination and originality.", "12. Seek input and collaboration from others to solve the problem. Emphasize teamwork, open communication, and leveraging the diverse perspectives and expertise of a group to come up with effective solutions.", "13. Use systems thinking: Consider the problem as part of a larger system and understanding the interconnectedness of various elements. Focuses on identifying the underlying causes, feedback loops, and interdependencies that influence the problem, and developing holistic solutions that address the system as a whole.", "14. Use Risk Analysis: Evaluate potential risks, uncertainties, and tradeoffs associated with different solutions or approaches to a problem. Emphasize assessing the potential consequences and likelihood of success or failure, and making informed decisions based on a balanced analysis of risks and benefits.", "15. Use Reflective Thinking: Step back from the problem, take the time for introspection and self-reflection. Examine personal biases, assumptions, and mental models that may influence problem-solving, and being open to learning from past experiences to improve future approaches.", "16. What is the core issue or problem that needs to be addressed?", "17. What are the underlying causes or factors contributing to the problem?", "18. Are there any potential solutions or strategies that have been tried before? If yes, what were the outcomes and lessons learned?", "19. What are the potential obstacles or challenges that might arise in solving this problem?", "20. Are there any relevant data or information that can provide insights into the problem? If yes, what data sources are available, and how can they be analyzed?", "21. Are there any stakeholders or individuals who are directly affected by the problem? What are their perspectives and needs?", "22. What resources (financial, human, technological, etc.) are needed to tackle the problem effectively?", "23. How can progress or success in solving the problem be measured or evaluated?", "24. What indicators or metrics can be used?", "25. Is the problem a technical or practical one that requires a specific expertise or skill set? Or is it more of a conceptual or theoretical problem?", "26. Does the problem involve a physical constraint, such as limited resources, infrastructure, or space?", "27. Is the problem related to human behavior, such as a social, cultural, or psychological issue?", "28. Does the problem involve decision-making or planning, where choices need to be made under uncertainty or with competing objectives?", "29. Is the problem an analytical one that requires data analysis, modeling, or optimization techniques?", "30. Is the problem a design challenge that requires creative solutions and innovation?", "31. Does the problem require addressing systemic or structural issues rather than just individual instances?", "32. Is the problem time-sensitive or urgent, requiring immediate attention and action?", "33. What kinds of solution typically are produced for this kind of problem specification?", "34. Given the problem specification and the current best solution, have a guess about other possible solutions." "35. Let’s imagine the current best solution is totally wrong, what other ways are there to think about the problem specification?" "36. What is the best way to modify this current best solution, given what you know about these kinds of problem specification?" "37. Ignoring the current best solution, create an entirely new solution to the problem." "38. Let’s think step by step ." "39. Let’s make a step by step plan and implement it with good notation and explanation.", ] _REASONING_MODULES = "\n".join(_REASONING_MODULES) SELECT_PRMOPT_TEMPLATE = PromptTemplate( "Given the task: {task}, which of the following reasoning modules are relevant? Do not elaborate on why.\n\n {reasoning_modules}" ) ADAPT_PROMPT_TEMPLATE = PromptTemplate( "Without working out the full solution, adapt the following reasoning modules to be specific to our task:\n{selected_modules}\n\nOur task:\n{task}" ) IMPLEMENT_PROMPT_TEMPLATE = PromptTemplate( "Without working out the full solution, create an actionable reasoning structure for the task using these adapted reasoning modules:\n{adapted_modules}\n\nTask Description:\n{task}" ) REASONING_PROMPT_TEMPLATE = PromptTemplate( "Using the following reasoning structure: {reasoning_structure}\n\nSolve this task, providing your final answer: {task}" )
## Designing the Workflow¶
SELF-DISCOVER consists of the following steps:
  1. Selecting a subset of given reasoning modules.
  2. Refine and adapt the subset of given reasoning modules based on the task.
  3. Create a reasoning structure for the task given the adapted reasoning modules.
  4. Generate a final answer for the task given the reasoning structure.


The following events are needed:
  1. `GetModulesEvent`: Triggered after a subset of modules are retrieved.
  2. `RefineModulesEvent`: Triggered after the modules are refined and adapted to the task.
  3. `ReasoningStructureEvent`: Triggered after the reasoning structure is generated.


In [ ]:
Copied!
```
from llama_index.core.workflow import Event


class GetModulesEvent(Event):
    """Event to get modules."""

    task: str
    modules: str


class RefineModulesEvent(Event):
    """Event to refine modules."""

    task: str
    refined_modules: str


class ReasoningStructureEvent(Event):
    """Event to create reasoning structure."""

    task: str
    reasoning_structure: str

```

from llama_index.core.workflow import Event class GetModulesEvent(Event): """Event to get modules.""" task: str modules: str class RefineModulesEvent(Event): """Event to refine modules.""" task: str refined_modules: str class ReasoningStructureEvent(Event): """Event to create reasoning structure.""" task: str reasoning_structure: str
Below is the code for the SELF-DISCOVER workflow:
In [ ]:
Copied!
```
from llama_index.core.workflow import (
    Workflow,
    Context,
    StartEvent,
    StopEvent,
    step,
)
from llama_index.core.llms import LLM


class SelfDiscoverWorkflow(Workflow):
    """Self discover workflow."""

    @step
    async def get_modules(
        self, ctx: Context, ev: StartEvent
    ) -> GetModulesEvent:
        """Get modules step."""
        # get input data, store llm into ctx
        task = ev.get("task")
        llm: LLM = ev.get("llm")

        if task is None or llm is None:
            raise ValueError("'task' and 'llm' arguments are required.")

        await ctx.store.set("llm", llm)

        # format prompt and get result from LLM
        prompt = SELECT_PRMOPT_TEMPLATE.format(
            task=task, reasoning_modules=_REASONING_MODULES
        )
        result = llm.complete(prompt)

        return GetModulesEvent(task=task, modules=str(result))

    @step
    async def refine_modules(
        self, ctx: Context, ev: GetModulesEvent
    ) -> RefineModulesEvent:
        """Refine modules step."""
        task = ev.task
        modules = ev.modules
        llm: LLM = await ctx.store.get("llm")

        # format prompt and get result
        prompt = ADAPT_PROMPT_TEMPLATE.format(
            task=task, selected_modules=modules
        )
        result = llm.complete(prompt)

        return RefineModulesEvent(task=task, refined_modules=str(result))

    @step
    async def create_reasoning_structure(
        self, ctx: Context, ev: RefineModulesEvent
    ) -> ReasoningStructureEvent:
        """Create reasoning structures step."""
        task = ev.task
        refined_modules = ev.refined_modules
        llm: LLM = await ctx.store.get("llm")

        # format prompt, get result
        prompt = IMPLEMENT_PROMPT_TEMPLATE.format(
            task=task, adapted_modules=refined_modules
        )
        result = llm.complete(prompt)

        return ReasoningStructureEvent(
            task=task, reasoning_structure=str(result)
        )

    @step
    async def get_final_result(
        self, ctx: Context, ev: ReasoningStructureEvent
    ) -> StopEvent:
        """Gets final result from reasoning structure event."""
        task = ev.task
        reasoning_structure = ev.reasoning_structure
        llm: LLM = await ctx.store.get("llm")

        # format prompt, get res
        prompt = REASONING_PROMPT_TEMPLATE.format(
            task=task, reasoning_structure=reasoning_structure
        )
        result = llm.complete(prompt)

        return StopEvent(result=result)

```

from llama_index.core.workflow import ( Workflow, Context, StartEvent, StopEvent, step, ) from llama_index.core.llms import LLM class SelfDiscoverWorkflow(Workflow): """Self discover workflow.""" @step async def get_modules( self, ctx: Context, ev: StartEvent ) -> GetModulesEvent: """Get modules step.""" # get input data, store llm into ctx task = ev.get("task") llm: LLM = ev.get("llm") if task is None or llm is None: raise ValueError("'task' and 'llm' arguments are required.") await ctx.store.set("llm", llm) # format prompt and get result from LLM prompt = SELECT_PRMOPT_TEMPLATE.format( task=task, reasoning_modules=_REASONING_MODULES ) result = llm.complete(prompt) return GetModulesEvent(task=task, modules=str(result)) @step async def refine_modules( self, ctx: Context, ev: GetModulesEvent ) -> RefineModulesEvent: """Refine modules step.""" task = ev.task modules = ev.modules llm: LLM = await ctx.store.get("llm") # format prompt and get result prompt = ADAPT_PROMPT_TEMPLATE.format( task=task, selected_modules=modules ) result = llm.complete(prompt) return RefineModulesEvent(task=task, refined_modules=str(result)) @step async def create_reasoning_structure( self, ctx: Context, ev: RefineModulesEvent ) -> ReasoningStructureEvent: """Create reasoning structures step.""" task = ev.task refined_modules = ev.refined_modules llm: LLM = await ctx.store.get("llm") # format prompt, get result prompt = IMPLEMENT_PROMPT_TEMPLATE.format( task=task, adapted_modules=refined_modules ) result = llm.complete(prompt) return ReasoningStructureEvent( task=task, reasoning_structure=str(result) ) @step async def get_final_result( self, ctx: Context, ev: ReasoningStructureEvent ) -> StopEvent: """Gets final result from reasoning structure event.""" task = ev.task reasoning_structure = ev.reasoning_structure llm: LLM = await ctx.store.get("llm") # format prompt, get res prompt = REASONING_PROMPT_TEMPLATE.format( task=task, reasoning_structure=reasoning_structure ) result = llm.complete(prompt) return StopEvent(result=result)
## Running the workflow¶
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI

workflow = SelfDiscoverWorkflow()
llm = OpenAI("gpt-4o")

```

from llama_index.llms.openai import OpenAI workflow = SelfDiscoverWorkflow() llm = OpenAI("gpt-4o")
In [ ]:
Copied!
```
from IPython.display import display, Markdown

task = "Michael has 15 oranges. He gives 4 oranges to his brother and trades 3 oranges for 6 apples with his neighbor. Later in the day, he realizes some of his oranges are spoiled, so he discards 2 of them. Then, Michael goes to the market and buys 12 more oranges and 5 more apples. If Michael decides to give 2 apples to his friend, how many oranges and apples does Michael have now?"
result = await workflow.run(task=task, llm=llm)
display(Markdown(str(result)))

```

from IPython.display import display, Markdown task = "Michael has 15 oranges. He gives 4 oranges to his brother and trades 3 oranges for 6 apples with his neighbor. Later in the day, he realizes some of his oranges are spoiled, so he discards 2 of them. Then, Michael goes to the market and buys 12 more oranges and 5 more apples. If Michael decides to give 2 apples to his friend, how many oranges and apples does Michael have now?" result = await workflow.run(task=task, llm=llm) display(Markdown(str(result)))
To solve the task of determining how many oranges and apples Michael has now, we will follow the structured reasoning approach and break down the problem into smaller, manageable parts. We will update the counts of oranges and apples step by step.
### Step-by-Step Plan:¶
  1. **Initial count of oranges:**
     * Michael starts with 15 oranges.
     * ( \text{Oranges} = 15 )
  2. **Oranges given to his brother:**
     * Michael gives 4 oranges to his brother.
     * ( \text{Oranges} = 15 - 4 = 11 )
  3. **Oranges traded for apples:**
     * Michael trades 3 oranges for 6 apples.
     * ( \text{Oranges} = 11 - 3 = 8 )
     * ( \text{Apples} = 0 + 6 = 6 )
  4. **Spoiled oranges discarded:**
     * Michael discards 2 spoiled oranges.
     * ( \text{Oranges} = 8 - 2 = 6 )
  5. **Oranges bought at the market:**
     * Michael buys 12 more oranges.
     * ( \text{Oranges} = 6 + 12 = 18 )
  6. **Initial count of apples:**
     * Michael initially had no apples.
     * ( \text{Apples} = 6 ) (from the trade)
  7. **Apples bought at the market:**
     * Michael buys 5 more apples.
     * ( \text{Apples} = 6 + 5 = 11 )
  8. **Apples given to his friend:**
     * Michael gives 2 apples to his friend.
     * ( \text{Apples} = 11 - 2 = 9 )


### Final counts:¶
  * **Oranges:** 18
  * **Apples:** 9


Therefore, Michael has 18 oranges and 9 apples now.
