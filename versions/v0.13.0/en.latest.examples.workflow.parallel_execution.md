# Parallel Execution of Same Event Example¶
In this example, we'll demonstrate how to use the workflow functionality to achieve similar capabilities while allowing parallel execution of multiple events of the same type.  
By setting the `num_workers` parameter in `@step` decorator, we can control the number of steps executed simultaneously, enabling efficient parallel processing.
# Installing Dependencies¶
First, we need to install the necessary dependencies:
  * LlamaIndex core for most functionalities
  * llama-index-utils-workflow for workflow capabilities


In [ ]:
Copied!
```
# %pip install llama-index-core llama-index-utils-workflow -q

```

# %pip install llama-index-core llama-index-utils-workflow -q
# Importing Required Libraries¶
After installing the dependencies, we can import the required libraries:
In [ ]:
Copied!
```
import asyncio
from llama_index.core.workflow import (
    step,
    Context,
    Workflow,
    Event,
    StartEvent,
    StopEvent,
)

```

import asyncio from llama_index.core.workflow import ( step, Context, Workflow, Event, StartEvent, StopEvent, )
We will create two workflows: one that can process multiple data items in parallel by using the `@step(num_workers=N)` decorator, and another without setting num_workers, for comparison.  
By using the `num_workers` parameter in the `@step` decorator, we can limit the number of steps executed simultaneously, thus controlling the level of parallelism. This approach is particularly suitable for scenarios that require processing similar tasks while managing resource usage.  
For example, you can execute multiple sub-queries at once, but please note that num_workers cannot be set without limits. It depends on your workload or token limits.
# Defining Event Types¶
We'll define two event types: one for input events to be processed, and another for processing results:
In [ ]:
Copied!
```
class ProcessEvent(Event):
    data: str


class ResultEvent(Event):
    result: str

```

class ProcessEvent(Event): data: str class ResultEvent(Event): result: str
# Creating Sequential and Parallel Workflows¶
Now, we'll create a SequentialWorkflow and a ParallelWorkflow class that includes three main steps:
  * start: Initialize and send multiple parallel events
  * process_data: Process data
  * combine_results: Collect and merge all processing results


In [ ]:
Copied!
```
import random


class SequentialWorkflow(Workflow):
    @step
    async def start(self, ctx: Context, ev: StartEvent) -> ProcessEvent:
        data_list = ["A", "B", "C"]
        await ctx.store.set("num_to_collect", len(data_list))
        for item in data_list:
            ctx.send_event(ProcessEvent(data=item))
        return None

    @step(num_workers=1)
    async def process_data(self, ev: ProcessEvent) -> ResultEvent:
        # Simulate some time-consuming processing
        processing_time = 2 + random.random()
        await asyncio.sleep(processing_time)
        result = f"Processed: {ev.data}"
        print(f"Completed processing: {ev.data}")
        return ResultEvent(result=result)

    @step
    async def combine_results(
        self, ctx: Context, ev: ResultEvent
    ) -> StopEvent | None:
        num_to_collect = await ctx.store.get("num_to_collect")
        results = ctx.collect_events(ev, [ResultEvent] * num_to_collect)
        if results is None:
            return None

        combined_result = ", ".join([event.result for event in results])
        return StopEvent(result=combined_result)


class ParallelWorkflow(Workflow):
    @step
    async def start(self, ctx: Context, ev: StartEvent) -> ProcessEvent:
        data_list = ["A", "B", "C"]
        await ctx.store.set("num_to_collect", len(data_list))
        for item in data_list:
            ctx.send_event(ProcessEvent(data=item))
        return None

    @step(num_workers=3)
    async def process_data(self, ev: ProcessEvent) -> ResultEvent:
        # Simulate some time-consuming processing
        processing_time = 2 + random.random()
        await asyncio.sleep(processing_time)
        result = f"Processed: {ev.data}"
        print(f"Completed processing: {ev.data}")
        return ResultEvent(result=result)

    @step
    async def combine_results(
        self, ctx: Context, ev: ResultEvent
    ) -> StopEvent | None:
        num_to_collect = await ctx.store.get("num_to_collect")
        results = ctx.collect_events(ev, [ResultEvent] * num_to_collect)
        if results is None:
            return None

        combined_result = ", ".join([event.result for event in results])
        return StopEvent(result=combined_result)

```

import random class SequentialWorkflow(Workflow): @step async def start(self, ctx: Context, ev: StartEvent) -> ProcessEvent: data_list = ["A", "B", "C"] await ctx.store.set("num_to_collect", len(data_list)) for item in data_list: ctx.send_event(ProcessEvent(data=item)) return None @step(num_workers=1) async def process_data(self, ev: ProcessEvent) -> ResultEvent: # Simulate some time-consuming processing processing_time = 2 + random.random() await asyncio.sleep(processing_time) result = f"Processed: {ev.data}" print(f"Completed processing: {ev.data}") return ResultEvent(result=result) @step async def combine_results( self, ctx: Context, ev: ResultEvent ) -> StopEvent | None: num_to_collect = await ctx.store.get("num_to_collect") results = ctx.collect_events(ev, [ResultEvent] * num_to_collect) if results is None: return None combined_result = ", ".join([event.result for event in results]) return StopEvent(result=combined_result) class ParallelWorkflow(Workflow): @step async def start(self, ctx: Context, ev: StartEvent) -> ProcessEvent: data_list = ["A", "B", "C"] await ctx.store.set("num_to_collect", len(data_list)) for item in data_list: ctx.send_event(ProcessEvent(data=item)) return None @step(num_workers=3) async def process_data(self, ev: ProcessEvent) -> ResultEvent: # Simulate some time-consuming processing processing_time = 2 + random.random() await asyncio.sleep(processing_time) result = f"Processed: {ev.data}" print(f"Completed processing: {ev.data}") return ResultEvent(result=result) @step async def combine_results( self, ctx: Context, ev: ResultEvent ) -> StopEvent | None: num_to_collect = await ctx.store.get("num_to_collect") results = ctx.collect_events(ev, [ResultEvent] * num_to_collect) if results is None: return None combined_result = ", ".join([event.result for event in results]) return StopEvent(result=combined_result)
In these two workflows:
  * The start method initializes and sends multiple ProcessEvent.
  * The process_data method uses
    * only the `@step` decorator in SequentialWorkflow
    * uses the `@step(num_workers=3)` decorator in ParallelWorkflow to limit the number of simultaneously executing workers to 3.
  * The combine_results method collects all processing results and merges them.


# Running the Workflow¶
Finally, we can create a main function to run our workflow:
In [ ]:
Copied!
```
import time

sequential_workflow = SequentialWorkflow()

print(
    "Start a sequential workflow without setting num_workers in the step of process_data"
)
start_time = time.time()
result = await sequential_workflow.run()
end_time = time.time()
print(f"Workflow result: {result}")
print(f"Time taken: {end_time - start_time} seconds")
print("-" * 30)

parallel_workflow = ParallelWorkflow()

print(
    "Start a parallel workflow with setting num_workers in the step of process_data"
)
start_time = time.time()
result = await parallel_workflow.run()
end_time = time.time()
print(f"Workflow result: {result}")
print(f"Time taken: {end_time - start_time} seconds")

```

import time sequential_workflow = SequentialWorkflow() print( "Start a sequential workflow without setting num_workers in the step of process_data" ) start_time = time.time() result = await sequential_workflow.run() end_time = time.time() print(f"Workflow result: {result}") print(f"Time taken: {end_time - start_time} seconds") print("-" * 30) parallel_workflow = ParallelWorkflow() print( "Start a parallel workflow with setting num_workers in the step of process_data" ) start_time = time.time() result = await parallel_workflow.run() end_time = time.time() print(f"Workflow result: {result}") print(f"Time taken: {end_time - start_time} seconds")
```
Start a sequential workflow without setting num_workers in the step of process_data
Completed processing: A
Completed processing: B
Completed processing: C
Workflow result: Processed: A, Processed: B, Processed: C
Time taken: 7.439495086669922 seconds
------------------------------
Start a parallel workflow with setting num_workers in the step of process_data
Completed processing: C
Completed processing: A
Completed processing: B
Workflow result: Processed: C, Processed: A, Processed: B
Time taken: 2.5881590843200684 seconds

```

# Note¶
  * Without setting `num_workers=1`, it might take a total of 6-9 seconds. By setting `num_workers=3`, the processing occurs in parallel, handling 3 items at a time, and only takes 2-3 seconds total.
  * In ParallelWorkflow, the order of the completed results may differ from the input order, depending on the completion time of the tasks.


This example demonstrates the execution speed with and without using num_workers, and how to implement parallel processing in a workflow. By setting num_workers, we can control the degree of parallelism, which is very useful for scenarios that need to balance performance and resource usage.
# Checkpointing¶
Checkpointing a parallel execution Workflow like the one defined above is also possible. To do so, we must wrap the `Workflow` with a `WorkflowCheckpointer` object and perfrom the runs with these instances. During the execution of the workflow, checkpoints are stored in this wrapper object and can be used for inspection and as starting points for run executions.
In [ ]:
Copied!
```
from llama_index.core.workflow.checkpointer import WorkflowCheckpointer

```

from llama_index.core.workflow.checkpointer import WorkflowCheckpointer
In [ ]:
Copied!
```
wflow_ckptr = WorkflowCheckpointer(workflow=parallel_workflow)
handler = wflow_ckptr.run()
await handler

```

wflow_ckptr = WorkflowCheckpointer(workflow=parallel_workflow) handler = wflow_ckptr.run() await handler
```
Completed processing: C
Completed processing: A
Completed processing: B

```

Out[ ]:
```
'Processed: C, Processed: A, Processed: B'
```

Checkpoints for the above run are stored in the `WorkflowCheckpointer.checkpoints` Dict attribute.
In [ ]:
Copied!
```
for run_id, ckpts in wflow_ckptr.checkpoints.items():
    print(f"Run: {run_id} has {[c.last_completed_step for c in ckpts]}")

```

for run_id, ckpts in wflow_ckptr.checkpoints.items(): print(f"Run: {run_id} has {[c.last_completed_step for c in ckpts]}")
```
Run: 90812bec-b571-4513-8ad5-aa957ad7d4fb has ['process_data', 'process_data', 'process_data', 'combine_results']

```

We can run from any of the checkpoints stored, using `WorkflowCheckpointer.run_from(checkpoint=...)` method. Let's take the first checkpoint that was stored after the first completion of "process_data" and run from it.
In [ ]:
Copied!
```
ckpt = wflow_ckptr.checkpoints[run_id][0]
handler = wflow_ckptr.run_from(ckpt)
await handler

```

ckpt = wflow_ckptr.checkpoints[run_id][0] handler = wflow_ckptr.run_from(ckpt) await handler
```
Completed processing: B
Completed processing: A

```

Out[ ]:
```
'Processed: C, Processed: B, Processed: A'
```

Invoking a `run_from` or `run` will create a new run entry in the `checkpoints` attribute. In the latest run from the specified checkpoint, we can see that only two more "process_data" steps and the final "combine_results" steps were left to be completed.
In [ ]:
Copied!
```
for run_id, ckpts in wflow_ckptr.checkpoints.items():
    print(f"Run: {run_id} has {[c.last_completed_step for c in ckpts]}")

```

for run_id, ckpts in wflow_ckptr.checkpoints.items(): print(f"Run: {run_id} has {[c.last_completed_step for c in ckpts]}")
```
Run: 90812bec-b571-4513-8ad5-aa957ad7d4fb has ['process_data', 'process_data', 'process_data', 'combine_results']
Run: 4e1d24cd-c672-4ed1-bb5b-b9f1a252abed has ['process_data', 'process_data', 'combine_results']

```

Now, if we use the checkpoint associated with the second completion of "process_data" of the same initial run as the starting point, then we should see a new entry that only has two steps: "process_data" and "combine_results".
In [ ]:
Copied!
```
# get the run_id of the first initial run
first_run_id = next(iter(wflow_ckptr.checkpoints.keys()))
first_run_id

```

# get the run_id of the first initial run first_run_id = next(iter(wflow_ckptr.checkpoints.keys())) first_run_id
Out[ ]:
```
'90812bec-b571-4513-8ad5-aa957ad7d4fb'
```

In [ ]:
Copied!
```
ckpt = wflow_ckptr.checkpoints[first_run_id][
    1
]  # checkpoint after the second "process_data" step
handler = wflow_ckptr.run_from(ckpt)
await handler

```

ckpt = wflow_ckptr.checkpoints[first_run_id][ 1 ] # checkpoint after the second "process_data" step handler = wflow_ckptr.run_from(ckpt) await handler
```
Completed processing: B

```

Out[ ]:
```
'Processed: C, Processed: A, Processed: B'
```

In [ ]:
Copied!
```
for run_id, ckpts in wflow_ckptr.checkpoints.items():
    print(f"Run: {run_id} has {[c.last_completed_step for c in ckpts]}")

```

for run_id, ckpts in wflow_ckptr.checkpoints.items(): print(f"Run: {run_id} has {[c.last_completed_step for c in ckpts]}")
```
Run: 90812bec-b571-4513-8ad5-aa957ad7d4fb has ['process_data', 'process_data', 'process_data', 'combine_results']
Run: 4e1d24cd-c672-4ed1-bb5b-b9f1a252abed has ['process_data', 'process_data', 'combine_results']
Run: e4f94fcd-9b78-4e28-8981-e0232d068f6e has ['process_data', 'combine_results']

```

Similarly, if we start with the checkpoint for the third completion of "process_data" of the initial run, then we should only see the final "combine_results" step.
In [ ]:
Copied!
```
ckpt = wflow_ckptr.checkpoints[first_run_id][
    2
]  # checkpoint after the third "process_data" step
handler = wflow_ckptr.run_from(ckpt)
await handler

```

ckpt = wflow_ckptr.checkpoints[first_run_id][ 2 ] # checkpoint after the third "process_data" step handler = wflow_ckptr.run_from(ckpt) await handler
Out[ ]:
```
'Processed: C, Processed: A, Processed: B'
```

In [ ]:
Copied!
```
for run_id, ckpts in wflow_ckptr.checkpoints.items():
    print(f"Run: {run_id} has {[c.last_completed_step for c in ckpts]}")

```

for run_id, ckpts in wflow_ckptr.checkpoints.items(): print(f"Run: {run_id} has {[c.last_completed_step for c in ckpts]}")
```
Run: 90812bec-b571-4513-8ad5-aa957ad7d4fb has ['process_data', 'process_data', 'process_data', 'combine_results']
Run: 4e1d24cd-c672-4ed1-bb5b-b9f1a252abed has ['process_data', 'process_data', 'combine_results']
Run: e4f94fcd-9b78-4e28-8981-e0232d068f6e has ['process_data', 'combine_results']
Run: c498a1a0-cf4c-4d80-a1e2-a175bb90b66d has ['combine_results']

```

