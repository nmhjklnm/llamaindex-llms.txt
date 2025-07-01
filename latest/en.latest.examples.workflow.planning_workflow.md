# Query Planning Workflow¶
In this notebook, we'll walk through an example of a query planning workflow.
This workflow is useful for any system that needs iterative planning to answer a user's query, as it decomposes a query into smaller steps, executes those steps, and aggregates the results.
Once a plan is executed, we can use the results to form a final response to the user's query or to form a new query plan if the current plan was not sufficient to answer the query.
## Setup¶
We will use OpenAI models, as well as llama-parse to load and parse documents.
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "sk-proj-..."
os.environ["LLAMA_CLOUD_API_KEY"] = "llx-..."

```

import os os.environ["OPENAI_API_KEY"] = "sk-proj-..." os.environ["LLAMA_CLOUD_API_KEY"] = "llx-..."
In [ ]:
Copied!
```
!mkdir -p "./data/sf_budgets/"
!wget "https://www.dropbox.com/scl/fi/xt3squt47djba0j7emmjb/2016-CSF_Budget_Book_2016_FINAL_WEB_with-cover-page.pdf?rlkey=xs064cjs8cb4wma6t5pw2u2bl&dl=0" -O "./data/sf_budgets/2016 - CSF_Budget_Book_2016_FINAL_WEB_with-cover-page.pdf"
!wget "https://www.dropbox.com/scl/fi/jvw59g5nscu1m7f96tjre/2017-Proposed-Budget-FY2017-18-FY2018-19_1.pdf?rlkey=v988oigs2whtcy87ti9wti6od&dl=0" -O "./data/sf_budgets/2017 - 2017-Proposed-Budget-FY2017-18-FY2018-19_1.pdf"
!wget "https://www.dropbox.com/scl/fi/izknlwmbs7ia0lbn7zzyx/2018-o0181-18.pdf?rlkey=p5nv2ehtp7272ege3m9diqhei&dl=0" -O "./data/sf_budgets/2018 - 2018-o0181-18.pdf"
!wget "https://www.dropbox.com/scl/fi/1rstqm9rh5u5fr0tcjnxj/2019-Proposed-Budget-FY2019-20-FY2020-21.pdf?rlkey=3s2ivfx7z9bev1r840dlpbcgg&dl=0" -O "./data/sf_budgets/2019 - 2019-Proposed-Budget-FY2019-20-FY2020-21.pdf"
!wget "https://www.dropbox.com/scl/fi/7teuwxrjdyvgw0n8jjvk0/2021-AAO-FY20-21-FY21-22-09-11-2020-FINAL.pdf?rlkey=6br3wzxwj5fv1f1l8e69nbmhk&dl=0" -O "./data/sf_budgets/2021 - 2021-AAO-FY20-21-FY21-22-09-11-2020-FINAL.pdf"
!wget "https://www.dropbox.com/scl/fi/zhgqch4n6xbv9skgcknij/2022-AAO-FY2021-22-FY2022-23-FINAL-20210730.pdf?rlkey=h78t65dfaz3mqbpbhl1u9e309&dl=0" -O "./data/sf_budgets/2022 - 2022-AAO-FY2021-22-FY2022-23-FINAL-20210730.pdf"
!wget "https://www.dropbox.com/scl/fi/vip161t63s56vd94neqlt/2023-CSF_Proposed_Budget_Book_June_2023_Master_Web.pdf?rlkey=hemoce3w1jsuf6s2bz87g549i&dl=0" -O "./data/sf_budgets/2023 - 2023-CSF_Proposed_Budget_Book_June_2023_Master_Web.pdf"

```

!mkdir -p "./data/sf_budgets/" !wget "https://www.dropbox.com/scl/fi/xt3squt47djba0j7emmjb/2016-CSF_Budget_Book_2016_FINAL_WEB_with-cover-page.pdf?rlkey=xs064cjs8cb4wma6t5pw2u2bl&dl=0" -O "./data/sf_budgets/2016 - CSF_Budget_Book_2016_FINAL_WEB_with-cover-page.pdf" !wget "https://www.dropbox.com/scl/fi/jvw59g5nscu1m7f96tjre/2017-Proposed-Budget-FY2017-18-FY2018-19_1.pdf?rlkey=v988oigs2whtcy87ti9wti6od&dl=0" -O "./data/sf_budgets/2017 - 2017-Proposed-Budget-FY2017-18-FY2018-19_1.pdf" !wget "https://www.dropbox.com/scl/fi/izknlwmbs7ia0lbn7zzyx/2018-o0181-18.pdf?rlkey=p5nv2ehtp7272ege3m9diqhei&dl=0" -O "./data/sf_budgets/2018 - 2018-o0181-18.pdf" !wget "https://www.dropbox.com/scl/fi/1rstqm9rh5u5fr0tcjnxj/2019-Proposed-Budget-FY2019-20-FY2020-21.pdf?rlkey=3s2ivfx7z9bev1r840dlpbcgg&dl=0" -O "./data/sf_budgets/2019 - 2019-Proposed-Budget-FY2019-20-FY2020-21.pdf" !wget "https://www.dropbox.com/scl/fi/7teuwxrjdyvgw0n8jjvk0/2021-AAO-FY20-21-FY21-22-09-11-2020-FINAL.pdf?rlkey=6br3wzxwj5fv1f1l8e69nbmhk&dl=0" -O "./data/sf_budgets/2021 - 2021-AAO-FY20-21-FY21-22-09-11-2020-FINAL.pdf" !wget "https://www.dropbox.com/scl/fi/zhgqch4n6xbv9skgcknij/2022-AAO-FY2021-22-FY2022-23-FINAL-20210730.pdf?rlkey=h78t65dfaz3mqbpbhl1u9e309&dl=0" -O "./data/sf_budgets/2022 - 2022-AAO-FY2021-22-FY2022-23-FINAL-20210730.pdf" !wget "https://www.dropbox.com/scl/fi/vip161t63s56vd94neqlt/2023-CSF_Proposed_Budget_Book_June_2023_Master_Web.pdf?rlkey=hemoce3w1jsuf6s2bz87g549i&dl=0" -O "./data/sf_budgets/2023 - 2023-CSF_Proposed_Budget_Book_June_2023_Master_Web.pdf"
## Workflow Definition¶
### Workflow Events¶
Since `Event` objects in workflows are just Pydantic models, we can use the function calling capabilities of OpenAI to dynamically define the execution of our workflow at runtime.
By predicting events, we are predicting the next step(s) in our workflow to run.
In [ ]:
Copied!
```
from pydantic import BaseModel, Field
from llama_index.core.workflow import Event


class QueryPlanItem(Event):
    """A single step in an execution plan for a RAG system."""

    name: str = Field(description="The name of the tool to use.")
    query: str = Field(
        description="A natural language search query for a RAG system."
    )


class QueryPlan(BaseModel):
    """A plan for a RAG system. After running the plan, we should have either enough information to answer the user's original query, or enough information to form a new query plan."""

    items: list[QueryPlanItem] = Field(
        description="A list of the QueryPlanItem objects in the plan."
    )

```

from pydantic import BaseModel, Field from llama_index.core.workflow import Event class QueryPlanItem(Event): """A single step in an execution plan for a RAG system.""" name: str = Field(description="The name of the tool to use.") query: str = Field( description="A natural language search query for a RAG system." ) class QueryPlan(BaseModel): """A plan for a RAG system. After running the plan, we should have either enough information to answer the user's original query, or enough information to form a new query plan.""" items: list[QueryPlanItem] = Field( description="A list of the QueryPlanItem objects in the plan." )
In addition to the query plan, we also need some workflow events to collect the results of the query plan items.
In [ ]:
Copied!
```
class QueryPlanItemResult(Event):
    """The result of a query plan item"""

    query: str
    result: str


class ExecutedPlanEvent(Event):
    """The result of a query plan"""

    result: str

```

class QueryPlanItemResult(Event): """The result of a query plan item""" query: str result: str class ExecutedPlanEvent(Event): """The result of a query plan""" result: str
### Workflow Definition¶
Now we can define our workflow. We will use an iterative process where we plan, execute, aggregate, and decide in an loop, until we have a final answer or a new query plan.
In [ ]:
Copied!
```
from llama_index.core.workflow import (
    Workflow,
    StopEvent,
    StartEvent,
    Context,
    step,
)
from llama_index.core.prompts import PromptTemplate
from llama_index.llms.openai import OpenAI


class QueryPlanningWorkflow(Workflow):
    llm = OpenAI(model="gpt-4o")
    planning_prompt = PromptTemplate(
        "Think step by step. Given an initial query, as well as information about the indexes you can query, return a plan for a RAG system.\n"
        "The plan should be a list of QueryPlanItem objects, where each object contains a query.\n"
        "The result of executing an entire plan should provide a result that is a substantial answer to the initial query, "
        "or enough information to form a new query plan.\n"
        "Sources you can query: {context}\n"
        "Initial query: {query}\n"
        "Plan:"
    )
    decision_prompt = PromptTemplate(
        "Given the following information, return a final response that satisfies the original query, or return 'PLAN' if you need to continue planning.\n"
        "Original query: {query}\n"
        "Current results: {results}\n"
    )

    @step
    async def planning_step(
        self, ctx: Context, ev: StartEvent | ExecutedPlanEvent
    ) -> QueryPlanItem | StopEvent:
        if isinstance(ev, StartEvent):
            # Initially, we need to plan
            query = ev.get("query")

            tools = ev.get("tools")

            await ctx.store.set("tools", {t.metadata.name: t for t in tools})
            await ctx.store.set("original_query", query)

            context_str = "\n".join(
                [
                    f"{i+1}. {tool.metadata.name}: {tool.metadata.description}"
                    for i, tool in enumerate(tools)
                ]
            )
            await ctx.store.set("context", context_str)

            query_plan = await self.llm.astructured_predict(
                QueryPlan,
                self.planning_prompt,
                context=context_str,
                query=query,
            )

            ctx.write_event_to_stream(
                Event(msg=f"Planning step: {query_plan}")
            )

            num_items = len(query_plan.items)
            await ctx.store.set("num_items", num_items)
            for item in query_plan.items:
                ctx.send_event(item)
        else:
            # If we've already gone through planning and executing, we need to decide
            # if we should continue planning or if we can stop and return a result.
            query = await ctx.store.get("original_query")
            current_results_str = ev.result

            decision = await self.llm.apredict(
                self.decision_prompt,
                query=query,
                results=current_results_str,
            )

            # Simple string matching to see if we need to keep planning or if we can stop.
            if "PLAN" in decision:
                context_str = await ctx.store.get("context")
                query_plan = await self.llm.astructured_predict(
                    QueryPlan,
                    self.planning_prompt,
                    context=context_str,
                    query=query,
                )

                ctx.write_event_to_stream(
                    Event(msg=f"Re-Planning step: {query_plan}")
                )

                num_items = len(query_plan.items)
                await ctx.store.set("num_items", num_items)
                for item in query_plan.items:
                    ctx.send_event(item)
            else:
                return StopEvent(result=decision)

    @step(num_workers=4)
    async def execute_item(
        self, ctx: Context, ev: QueryPlanItem
    ) -> QueryPlanItemResult:
        tools = await ctx.store.get("tools")
        tool = tools[ev.name]

        ctx.write_event_to_stream(
            Event(
                msg=f"Querying tool {tool.metadata.name} with query: {ev.query}"
            )
        )

        result = await tool.acall(ev.query)

        ctx.write_event_to_stream(
            Event(msg=f"Tool {tool.metadata.name} returned: {result}")
        )

        return QueryPlanItemResult(query=ev.query, result=str(result))

    @step
    async def aggregate_results(
        self, ctx: Context, ev: QueryPlanItemResult
    ) -> ExecutedPlanEvent:
        # We need to collect the results of the query plan items to aggregate them.
        num_items = await ctx.store.get("num_items")
        results = ctx.collect_events(ev, [QueryPlanItemResult] * num_items)

        # collect_events returns None if not all events were found
        # return and wait for the remaining events to come in.
        if results is None:
            return

        aggregated_result = "\n------\n".join(
            [
                f"{i+1}. {result.query}: {result.result}"
                for i, result in enumerate(results)
            ]
        )
        return ExecutedPlanEvent(result=aggregated_result)

```

from llama_index.core.workflow import ( Workflow, StopEvent, StartEvent, Context, step, ) from llama_index.core.prompts import PromptTemplate from llama_index.llms.openai import OpenAI class QueryPlanningWorkflow(Workflow): llm = OpenAI(model="gpt-4o") planning_prompt = PromptTemplate( "Think step by step. Given an initial query, as well as information about the indexes you can query, return a plan for a RAG system.\n" "The plan should be a list of QueryPlanItem objects, where each object contains a query.\n" "The result of executing an entire plan should provide a result that is a substantial answer to the initial query, " "or enough information to form a new query plan.\n" "Sources you can query: {context}\n" "Initial query: {query}\n" "Plan:" ) decision_prompt = PromptTemplate( "Given the following information, return a final response that satisfies the original query, or return 'PLAN' if you need to continue planning.\n" "Original query: {query}\n" "Current results: {results}\n" ) @step async def planning_step( self, ctx: Context, ev: StartEvent | ExecutedPlanEvent ) -> QueryPlanItem | StopEvent: if isinstance(ev, StartEvent): # Initially, we need to plan query = ev.get("query") tools = ev.get("tools") await ctx.store.set("tools", {t.metadata.name: t for t in tools}) await ctx.store.set("original_query", query) context_str = "\n".join( [ f"{i+1}. {tool.metadata.name}: {tool.metadata.description}" for i, tool in enumerate(tools) ] ) await ctx.store.set("context", context_str) query_plan = await self.llm.astructured_predict( QueryPlan, self.planning_prompt, context=context_str, query=query, ) ctx.write_event_to_stream( Event(msg=f"Planning step: {query_plan}") ) num_items = len(query_plan.items) await ctx.store.set("num_items", num_items) for item in query_plan.items: ctx.send_event(item) else: # If we've already gone through planning and executing, we need to decide # if we should continue planning or if we can stop and return a result. query = await ctx.store.get("original_query") current_results_str = ev.result decision = await self.llm.apredict( self.decision_prompt, query=query, results=current_results_str, ) # Simple string matching to see if we need to keep planning or if we can stop. if "PLAN" in decision: context_str = await ctx.store.get("context") query_plan = await self.llm.astructured_predict( QueryPlan, self.planning_prompt, context=context_str, query=query, ) ctx.write_event_to_stream( Event(msg=f"Re-Planning step: {query_plan}") ) num_items = len(query_plan.items) await ctx.store.set("num_items", num_items) for item in query_plan.items: ctx.send_event(item) else: return StopEvent(result=decision) @step(num_workers=4) async def execute_item( self, ctx: Context, ev: QueryPlanItem ) -> QueryPlanItemResult: tools = await ctx.store.get("tools") tool = tools[ev.name] ctx.write_event_to_stream( Event( msg=f"Querying tool {tool.metadata.name} with query: {ev.query}" ) ) result = await tool.acall(ev.query) ctx.write_event_to_stream( Event(msg=f"Tool {tool.metadata.name} returned: {result}") ) return QueryPlanItemResult(query=ev.query, result=str(result)) @step async def aggregate_results( self, ctx: Context, ev: QueryPlanItemResult ) -> ExecutedPlanEvent: # We need to collect the results of the query plan items to aggregate them. num_items = await ctx.store.get("num_items") results = ctx.collect_events(ev, [QueryPlanItemResult] * num_items) # collect_events returns None if not all events were found # return and wait for the remaining events to come in. if results is None: return aggregated_result = "\n------\n".join( [ f"{i+1}. {result.query}: {result.result}" for i, result in enumerate(results) ] ) return ExecutedPlanEvent(result=aggregated_result)
## Loading Data¶
Here, we use `llama-parse` to load and parse documents, and create an index for each year's budget.
In [ ]:
Copied!
```
from llama_parse import LlamaParse

parser = LlamaParse(fast_mode=True)

```

from llama_parse import LlamaParse parser = LlamaParse(fast_mode=True)
In [ ]:
Copied!
```
from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
)
from llama_index.core.tools import QueryEngineTool

folder = "./data/sf_budgets/"
files = os.listdir(folder)

query_engine_tools = []
for file in files:
    year = file.split(" - ")[0]
    index_persist_path = f"./storage/budget-{year}/"

    if os.path.exists(index_persist_path):
        storage_context = StorageContext.from_defaults(
            persist_dir=index_persist_path
        )
        index = load_index_from_storage(storage_context)
    else:
        documents = await parser.aload_data(folder + file)
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(index_persist_path)

    engine = index.as_query_engine()
    query_engine_tools.append(
        QueryEngineTool.from_defaults(
            engine,
            name=f"budget_{year}",
            description=f"Information about San Francisco's budget in {year}",
        )
    )

```

from llama_index.core import ( VectorStoreIndex, StorageContext, load_index_from_storage, ) from llama_index.core.tools import QueryEngineTool folder = "./data/sf_budgets/" files = os.listdir(folder) query_engine_tools = [] for file in files: year = file.split(" - ")[0] index_persist_path = f"./storage/budget-{year}/" if os.path.exists(index_persist_path): storage_context = StorageContext.from_defaults( persist_dir=index_persist_path ) index = load_index_from_storage(storage_context) else: documents = await parser.aload_data(folder + file) index = VectorStoreIndex.from_documents(documents) index.storage_context.persist(index_persist_path) engine = index.as_query_engine() query_engine_tools.append( QueryEngineTool.from_defaults( engine, name=f"budget_{year}", description=f"Information about San Francisco's budget in {year}", ) )
## Testing out the Workflow¶
Let's test out our workflow with a few queries.
Since we wrote a few stream events, we can see the execution of the workflow as it runs.
In [ ]:
Copied!
```
workflow = QueryPlanningWorkflow(verbose=False, timeout=120)

```

workflow = QueryPlanningWorkflow(verbose=False, timeout=120)
In [ ]:
Copied!
```
# run the workflow
handler = workflow.run(
    query="How has the total amount of San Francisco's budget changed from 2016 to 2023?",
    tools=query_engine_tools,
)

# stream the events as they come in
async for event in handler.stream_events():
    if hasattr(event, "msg"):
        print(event.msg)

# get the final result
result = await handler

```

# run the workflow handler = workflow.run( query="How has the total amount of San Francisco's budget changed from 2016 to 2023?", tools=query_engine_tools, ) # stream the events as they come in async for event in handler.stream_events(): if hasattr(event, "msg"): print(event.msg) # get the final result result = await handler
```
Planning step: items=[QueryPlanItem(name='budget_2016', query="What was the total amount of San Francisco's budget in 2016?"), QueryPlanItem(name='budget_2017', query="What was the total amount of San Francisco's budget in 2017?"), QueryPlanItem(name='budget_2018', query="What was the total amount of San Francisco's budget in 2018?"), QueryPlanItem(name='budget_2019', query="What was the total amount of San Francisco's budget in 2019?"), QueryPlanItem(name='budget_2021', query="What was the total amount of San Francisco's budget in 2021?"), QueryPlanItem(name='budget_2022', query="What was the total amount of San Francisco's budget in 2022?"), QueryPlanItem(name='budget_2023', query="What was the total amount of San Francisco's budget in 2023?")]
Querying tool budget_2016 with query: What was the total amount of San Francisco's budget in 2016?
Querying tool budget_2017 with query: What was the total amount of San Francisco's budget in 2017?
Querying tool budget_2018 with query: What was the total amount of San Francisco's budget in 2018?
Querying tool budget_2019 with query: What was the total amount of San Francisco's budget in 2019?
Tool budget_2019 returned: The total amount of San Francisco's budget in 2019 was $12.3 billion.
Querying tool budget_2021 with query: What was the total amount of San Francisco's budget in 2021?
Tool budget_2018 returned: The total amount of San Francisco's budget in 2018 was $2,169,893 in thousands of dollars.
Querying tool budget_2022 with query: What was the total amount of San Francisco's budget in 2022?
Tool budget_2017 returned: The total amount of San Francisco's budget in 2017 was $10.1 billion.
Querying tool budget_2023 with query: What was the total amount of San Francisco's budget in 2023?
Tool budget_2016 returned: The total amount of San Francisco's budget in 2016 was $9.6 billion.
Tool budget_2021 returned: The total amount of San Francisco's budget in 2021 was $126,960,000.
Tool budget_2022 returned: The total amount of San Francisco's budget in 2022 was $13,248,709,511.
Tool budget_2023 returned: The total amount of San Francisco's budget in 2023 was $14.613 billion.

```

In [ ]:
Copied!
```
print(str(result))

```

print(str(result))
```
The total amount of San Francisco's budget has changed from $9.6 billion in 2016 to $14.613 billion in 2023. This represents an increase of $5.013 billion over the seven-year period.

```

In [ ]:
Copied!
```
# run the workflow again, with a new query
handler = workflow.run(
    query="What were the major spending categories in the 2023 budget vs. 2016?",
    tools=query_engine_tools,
)

# stream the events as they come in
async for event in handler.stream_events():
    if hasattr(event, "msg"):
        print(event.msg)

# get the final result
result = await handler

```

# run the workflow again, with a new query handler = workflow.run( query="What were the major spending categories in the 2023 budget vs. 2016?", tools=query_engine_tools, ) # stream the events as they come in async for event in handler.stream_events(): if hasattr(event, "msg"): print(event.msg) # get the final result result = await handler
```
Planning step: items=[QueryPlanItem(name='budget_2023', query='What were the major spending categories in the San Francisco 2023 budget?'), QueryPlanItem(name='budget_2016', query='What were the major spending categories in the San Francisco 2016 budget?')]
Querying tool budget_2023 with query: What were the major spending categories in the San Francisco 2023 budget?
Querying tool budget_2016 with query: What were the major spending categories in the San Francisco 2016 budget?
Tool budget_2016 returned: Public Protection, Public Works, Transportation & Commerce, Human Welfare & Neighborhood Development, Community Health, Culture & Recreation, General Administration & Finance, General City Responsibilities.
Tool budget_2023 returned: The major spending categories in the San Francisco 2023 budget were Community Health, Culture & Recreation, General Administration & Finance, General City Responsibilities, Human Welfare & Neighborhood Development, Public Protection, and Public Works, Transportation & Commerce.

```

In [ ]:
Copied!
```
print(str(result))

```

print(str(result))
```
The major spending categories in the San Francisco 2023 budget were Community Health, Culture & Recreation, General Administration & Finance, General City Responsibilities, Human Welfare & Neighborhood Development, Public Protection, and Public Works, Transportation & Commerce. In comparison, the major spending categories in the 2016 budget were Public Protection, Public Works, Transportation & Commerce, Human Welfare & Neighborhood Development, Community Health, Culture & Recreation, General Administration & Finance, and General City Responsibilities.

```

