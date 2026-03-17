# Checkpointing Workflow Runs¶
In this notebook, we demonstrate how to checkpoint `Workflow` runs via a `WorkflowCheckpointer` object. We also show how we can view all of the checkpoints that are stored in this object and finally how we can use a checkpoint as the starting point of a new run.
## Define a Workflow¶
In [ ]:
Copied!
```
import os

api_key = os.environ.get("OPENAI_API_KEY")

```

import os api_key = os.environ.get("OPENAI_API_KEY")
In [ ]:
Copied!
```
from llama_index.core.workflow import (
    Workflow,
    step,
    StartEvent,
    StopEvent,
    Event,
    Context,
)
from llama_index.llms.openai import OpenAI


class JokeEvent(Event):
    joke: str


class JokeFlow(Workflow):
    llm = OpenAI(api_key=api_key)

    @step
    async def generate_joke(self, ev: StartEvent) -> JokeEvent:
        topic = ev.topic

        prompt = f"Write your best joke about {topic}."
        response = await self.llm.acomplete(prompt)
        return JokeEvent(joke=str(response))

    @step
    async def critique_joke(self, ev: JokeEvent) -> StopEvent:
        joke = ev.joke

        prompt = f"Give a thorough analysis and critique of the following joke: {joke}"
        response = await self.llm.acomplete(prompt)
        return StopEvent(result=str(response))

```

from llama_index.core.workflow import ( Workflow, step, StartEvent, StopEvent, Event, Context, ) from llama_index.llms.openai import OpenAI class JokeEvent(Event): joke: str class JokeFlow(Workflow): llm = OpenAI(api_key=api_key) @step async def generate_joke(self, ev: StartEvent) -> JokeEvent: topic = ev.topic prompt = f"Write your best joke about {topic}." response = await self.llm.acomplete(prompt) return JokeEvent(joke=str(response)) @step async def critique_joke(self, ev: JokeEvent) -> StopEvent: joke = ev.joke prompt = f"Give a thorough analysis and critique of the following joke: {joke}" response = await self.llm.acomplete(prompt) return StopEvent(result=str(response))
## Define a WorkflowCheckpointer Object¶
In [ ]:
Copied!
```
from llama_index.core.workflow.checkpointer import WorkflowCheckpointer

```

from llama_index.core.workflow.checkpointer import WorkflowCheckpointer
In [ ]:
Copied!
```
# instantiate Jokeflow
workflow = JokeFlow()
wflow_ckptr = WorkflowCheckpointer(workflow=workflow)

```

# instantiate Jokeflow workflow = JokeFlow() wflow_ckptr = WorkflowCheckpointer(workflow=workflow)
## Run the Workflow from the WorkflowCheckpointer¶
The `WorkflowCheckpointer.run()` method is a wrapper over the `Workflow.run()` method, which injects a checkpointer callback in order to create and store checkpoints. Note that checkpoints are created at the completion of a step, and that the data stored in checkpoints are:
  * `last_completed_step`: The name of the last completed step
  * `input_event`: The input event to this last completed step
  * `output_event`: The event outputted by this last completed step
  * `ctx_state`: a snapshot of the attached `Context`


In [ ]:
Copied!
```
handler = wflow_ckptr.run(
    topic="chemistry",
)
await handler

```

handler = wflow_ckptr.run( topic="chemistry", ) await handler
Out[ ]:
```
'This joke plays on the double meaning of the word "rates," which can refer to both the cost of something and the passage of time. The punchline suggests that chemists prefer nitrates because they are less expensive than day rates, implying that chemists are frugal or cost-conscious individuals.\n\nOverall, the joke is clever and plays on a pun that is likely to be appreciated by those familiar with chemistry and the concept of nitrates. However, the humor may be lost on those who are not well-versed in chemistry terminology. Additionally, the joke relies on a somewhat simplistic play on words, which may not be as engaging or humorous to some audiences.\n\nIn terms of structure, the joke follows a classic setup and punchline format, with the punchline providing a surprising twist on the initial premise. The delivery of the joke may also play a role in its effectiveness, as timing and tone can greatly impact the humor of a joke.\n\nOverall, while the joke may appeal to a specific audience and demonstrate some clever wordplay, it may not have universal appeal and may be considered somewhat niche in its humor.'
```

We can view all of the checkpoints via the `.checkpoints` attribute, which is dictionary with keys representing the `run_id` of the run and whose values are the list of checkpoints stored for the run.
In [ ]:
Copied!
```
wflow_ckptr.checkpoints

```

wflow_ckptr.checkpoints
Out[ ]:
```
{'483eccdd-a035-42cc-b596-cd33d42938a7': [Checkpoint(id_='d5acd098-47e2-4acf-9520-9ca06ee4e238', last_completed_step='generate_joke', input_event=StartEvent(), output_event=JokeEvent(joke="Why do chemists like nitrates so much?\n\nBecause they're cheaper than day rates!"), ctx_state={'globals': {}, 'streaming_queue': '[]', 'queues': {'_done': '[]', 'critique_joke': '[]', 'generate_joke': '[]'}, 'stepwise': False, 'events_buffer': {}, 'in_progress': {'generate_joke': []}, 'accepted_events': [('generate_joke', 'StartEvent'), ('critique_joke', 'JokeEvent')], 'broker_log': ['{"__is_pydantic": true, "value": {"_data": {"topic": "chemistry", "store_checkpoints": false}}, "qualified_name": "llama_index.core.workflow.events.StartEvent"}'], 'is_running': True}),
  Checkpoint(id_='288c3e54-292b-4c7e-aed8-662537508b46', last_completed_step='critique_joke', input_event=JokeEvent(joke="Why do chemists like nitrates so much?\n\nBecause they're cheaper than day rates!"), output_event=StopEvent(result='This joke plays on the double meaning of the word "rates," which can refer to both the cost of something and the passage of time. The punchline suggests that chemists prefer nitrates because they are less expensive than day rates, implying that chemists are frugal or cost-conscious individuals.\n\nOverall, the joke is clever and plays on a pun that is likely to be appreciated by those familiar with chemistry and the concept of nitrates. However, the humor may be lost on those who are not well-versed in chemistry terminology. Additionally, the joke relies on a somewhat simplistic play on words, which may not be as engaging or humorous to some audiences.\n\nIn terms of structure, the joke follows a classic setup and punchline format, with the punchline providing a surprising twist on the initial premise. The delivery of the joke may also play a role in its effectiveness, as timing and tone can greatly impact the humor of a joke.\n\nOverall, while the joke may appeal to a specific audience and demonstrate some clever wordplay, it may not have universal appeal and may be considered somewhat niche in its humor.'), ctx_state={'globals': {}, 'streaming_queue': '[]', 'queues': {'_done': '[]', 'critique_joke': '[]', 'generate_joke': '[]'}, 'stepwise': False, 'events_buffer': {}, 'in_progress': {'generate_joke': [], 'critique_joke': []}, 'accepted_events': [('generate_joke', 'StartEvent'), ('critique_joke', 'JokeEvent')], 'broker_log': ['{"__is_pydantic": true, "value": {"_data": {"topic": "chemistry", "store_checkpoints": false}}, "qualified_name": "llama_index.core.workflow.events.StartEvent"}', '{"__is_pydantic": true, "value": {"joke": "Why do chemists like nitrates so much?\\n\\nBecause they\'re cheaper than day rates!"}, "qualified_name": "__main__.JokeEvent"}'], 'is_running': True})]}
```

In [ ]:
Copied!
```
for run_id, ckpts in wflow_ckptr.checkpoints.items():
    print(f"Run: {run_id} has {len(ckpts)} stored checkpoints")

```

for run_id, ckpts in wflow_ckptr.checkpoints.items(): print(f"Run: {run_id} has {len(ckpts)} stored checkpoints")
```
Run: 483eccdd-a035-42cc-b596-cd33d42938a7 has 2 stored checkpoints

```

## Filtering the Checkpoints¶
The `WorkflowCheckpointer` object also has a `.filter_checkpoints()` method that allows us to filter via:
  * The name of the last completed step by speciying the param `last_completed_step`
  * The event type of the last completed step's output event by specifying `output_event_type`
  * Similarly, the event type of the last completed step's input event by specifying `input_event_type`


Specifying multiple of these filters will be combined by the "AND" operator.
Let's test this functionality out, but first we'll make things a bit more interesting by running a couple of more runs with our `Workflow`.
In [ ]:
Copied!
```
additional_topics = ["biology", "history"]

for topic in additional_topics:
    handler = wflow_ckptr.run(topic=topic)
    await handler

```

additional_topics = ["biology", "history"] for topic in additional_topics: handler = wflow_ckptr.run(topic=topic) await handler
In [ ]:
Copied!
```
for run_id, ckpts in wflow_ckptr.checkpoints.items():
    print(f"Run: {run_id} has {len(ckpts)} stored checkpoints")

```

for run_id, ckpts in wflow_ckptr.checkpoints.items(): print(f"Run: {run_id} has {len(ckpts)} stored checkpoints")
```
Run: 483eccdd-a035-42cc-b596-cd33d42938a7 has 2 stored checkpoints
Run: e112bca9-637c-4492-a8aa-926c302c99d4 has 2 stored checkpoints
Run: 7a59c918-90a3-47f8-a818-71e45897ae39 has 2 stored checkpoints

```

In [ ]:
Copied!
```
# Filter by the name of last completed step
checkpoints_right_after_generate_joke_step = wflow_ckptr.filter_checkpoints(
    last_completed_step="generate_joke",
)

# checkpoint ids
[ckpt for ckpt in checkpoints_right_after_generate_joke_step]

```

# Filter by the name of last completed step checkpoints_right_after_generate_joke_step = wflow_ckptr.filter_checkpoints( last_completed_step="generate_joke", ) # checkpoint ids [ckpt for ckpt in checkpoints_right_after_generate_joke_step]
Out[ ]:
```
[Checkpoint(id_='d5acd098-47e2-4acf-9520-9ca06ee4e238', last_completed_step='generate_joke', input_event=StartEvent(), output_event=JokeEvent(joke="Why do chemists like nitrates so much?\n\nBecause they're cheaper than day rates!"), ctx_state={'globals': {}, 'streaming_queue': '[]', 'queues': {'_done': '[]', 'critique_joke': '[]', 'generate_joke': '[]'}, 'stepwise': False, 'events_buffer': {}, 'in_progress': {'generate_joke': []}, 'accepted_events': [('generate_joke', 'StartEvent'), ('critique_joke', 'JokeEvent')], 'broker_log': ['{"__is_pydantic": true, "value": {"_data": {"topic": "chemistry", "store_checkpoints": false}}, "qualified_name": "llama_index.core.workflow.events.StartEvent"}'], 'is_running': True}),
 Checkpoint(id_='87865641-14e7-4eb0-bb62-4c211567acfc', last_completed_step='generate_joke', input_event=StartEvent(), output_event=JokeEvent(joke="Why did the biologist break up with the mathematician?\n\nBecause they couldn't find a common denominator!"), ctx_state={'globals': {}, 'streaming_queue': '[]', 'queues': {'_done': '[]', 'critique_joke': '[]', 'generate_joke': '[]'}, 'stepwise': False, 'events_buffer': {}, 'in_progress': {'generate_joke': []}, 'accepted_events': [('generate_joke', 'StartEvent'), ('critique_joke', 'JokeEvent')], 'broker_log': ['{"__is_pydantic": true, "value": {"_data": {"topic": "biology"}}, "qualified_name": "llama_index.core.workflow.events.StartEvent"}'], 'is_running': True}),
 Checkpoint(id_='69a99535-d45c-46b4-a1f4-d3ecc128cb08', last_completed_step='generate_joke', input_event=StartEvent(), output_event=JokeEvent(joke='Why did the history teacher go to the beach?\n\nTo catch some waves of the past!'), ctx_state={'globals': {}, 'streaming_queue': '[]', 'queues': {'_done': '[]', 'critique_joke': '[]', 'generate_joke': '[]'}, 'stepwise': False, 'events_buffer': {}, 'in_progress': {'generate_joke': []}, 'accepted_events': [('generate_joke', 'StartEvent'), ('critique_joke', 'JokeEvent')], 'broker_log': ['{"__is_pydantic": true, "value": {"_data": {"topic": "history"}}, "qualified_name": "llama_index.core.workflow.events.StartEvent"}'], 'is_running': True})]
```

## Re-Run Workflow from a specific checkpoint¶
To run from a chosen `Checkpoint` we can use the `WorkflowCheckpointer.run_from()` method. NOTE that doing so will lead to a new `run` and it's checkpoints if enabled will be stored under the newly assigned `run_id`.
In [ ]:
Copied!
```
# can work with a new instance
new_workflow_instance = JokeFlow()
wflow_ckptr.workflow = new_workflow_instance

ckpt = checkpoints_right_after_generate_joke_step[0]

handler = wflow_ckptr.run_from(checkpoint=ckpt)
await handler

```

# can work with a new instance new_workflow_instance = JokeFlow() wflow_ckptr.workflow = new_workflow_instance ckpt = checkpoints_right_after_generate_joke_step[0] handler = wflow_ckptr.run_from(checkpoint=ckpt) await handler
Out[ ]:
```
'Analysis:\nThis joke plays on the double meaning of the word "rates," which can refer to both the cost of something and the passage of time. In this case, the joke suggests that chemists prefer nitrates because they are less expensive than day rates, implying that chemists are frugal or cost-conscious individuals.\n\nCritique:\n- Clever wordplay: The joke relies on a clever play on words, which can be entertaining for those who appreciate puns and linguistic humor.\n- Niche audience: The humor in this joke may be more appreciated by individuals with a background in chemistry or a specific interest in science, as the punchline relies on knowledge of chemical compounds.\n- Lack of universal appeal: The joke may not resonate with a general audience who may not understand the reference to nitrates or the significance of their cost compared to day rates.\n- Lack of depth: While the joke is amusing on a surface level, it may be considered somewhat shallow or simplistic compared to more nuanced or thought-provoking humor.\n\nOverall, the joke is a light-hearted play on words that may appeal to individuals with a specific interest in chemistry or wordplay. However, its niche appeal and lack of universal relevance may limit its effectiveness as a joke for a broader audience.'
```

In [ ]:
Copied!
```
for run_id, ckpts in wflow_ckptr.checkpoints.items():
    print(f"Run: {run_id} has {len(ckpts)} stored checkpoints")

```

for run_id, ckpts in wflow_ckptr.checkpoints.items(): print(f"Run: {run_id} has {len(ckpts)} stored checkpoints")
```
Run: 483eccdd-a035-42cc-b596-cd33d42938a7 has 2 stored checkpoints
Run: e112bca9-637c-4492-a8aa-926c302c99d4 has 2 stored checkpoints
Run: 7a59c918-90a3-47f8-a818-71e45897ae39 has 2 stored checkpoints
Run: 9dccfda3-b5bf-4771-8293-efd3e3a275a6 has 1 stored checkpoints

```

Since we've executed from the checkpoint that represents the end of "generate_joke" step, there is only one additional checkpoint (i.e., that for the completion of step "critique_joke") that gets stored in the last partial run.
## Specifying Which Steps To Checkpoint¶
By default all steps of the attached workflow (excluding the "_done" step) will be checkpointed. You can see which steps are enabled for checkpointing via the `enabled_checkpoints` attribute.
In [ ]:
Copied!
```
wflow_ckptr.enabled_checkpoints

```

wflow_ckptr.enabled_checkpoints
Out[ ]:
```
{'critique_joke', 'generate_joke'}
```

To disable a step for checkpointing, we can use the `.disable_checkpoint()` method
In [ ]:
Copied!
```
wflow_ckptr.disable_checkpoint(step="critique_joke")

```

wflow_ckptr.disable_checkpoint(step="critique_joke")
In [ ]:
Copied!
```
handler = wflow_ckptr.run(topic="cars")
await handler

```

handler = wflow_ckptr.run(topic="cars") await handler
Out[ ]:
```
"Analysis:\nThis joke plays on the common stereotype that mechanics are overly critical and nitpicky when it comes to fixing cars. The humor comes from the unexpected twist of the car being the one to break up with the mechanic, rather than the other way around. The punchline is clever and plays on the idea of a relationship ending due to constant criticism.\n\nCritique:\nOverall, this joke is light-hearted and easy to understand. It relies on a simple pun and doesn't require much thought to appreciate. However, the humor may be seen as somewhat predictable and not particularly original. The joke also perpetuates the stereotype of mechanics being overly critical, which may not sit well with some people in the automotive industry. Additionally, the joke may not be as universally funny as some other jokes, as it relies on a specific understanding of the relationship between cars and mechanics. Overall, while the joke is amusing, it may not be considered particularly groundbreaking or memorable."
```

In [ ]:
Copied!
```
for run_id, ckpts in wflow_ckptr.checkpoints.items():
    print(
        f"Run: {run_id} has stored checkpoints for steps {[c.last_completed_step for c in ckpts]}"
    )

```

for run_id, ckpts in wflow_ckptr.checkpoints.items(): print( f"Run: {run_id} has stored checkpoints for steps {[c.last_completed_step for c in ckpts]}" )
```
Run: 483eccdd-a035-42cc-b596-cd33d42938a7 has stored checkpoints for steps ['generate_joke', 'critique_joke']
Run: e112bca9-637c-4492-a8aa-926c302c99d4 has stored checkpoints for steps ['generate_joke', 'critique_joke']
Run: 7a59c918-90a3-47f8-a818-71e45897ae39 has stored checkpoints for steps ['generate_joke', 'critique_joke']
Run: 9dccfda3-b5bf-4771-8293-efd3e3a275a6 has stored checkpoints for steps ['critique_joke']
Run: 6390e2ce-63f4-44a3-8a75-64ccb765abfd has stored checkpoints for steps ['generate_joke']

```

And we can turn checkpointing back on by using the `.enable_checkpoint()` method
In [ ]:
Copied!
```
wflow_ckptr.enable_checkpoint(step="critique_joke")

```

wflow_ckptr.enable_checkpoint(step="critique_joke")
In [ ]:
Copied!
```
handler = wflow_ckptr.run(topic="cars")
await handler

```

handler = wflow_ckptr.run(topic="cars") await handler
Out[ ]:
```
'Analysis:\nThis joke plays on the common stereotype that mechanics are overly critical and nitpicky when it comes to fixing cars. The humor comes from the unexpected twist of the car being the one to break up with the mechanic, rather than the other way around. The joke also cleverly uses the term "nitpicking" in a literal sense, as in picking at the nit (small details) of the car.\n\nCritique:\nWhile the joke is clever and plays on a well-known stereotype, it may not be the most original or groundbreaking joke. The punchline is somewhat predictable and relies on a common trope about mechanics. Additionally, the joke may not be universally relatable or understood by all audiences, as it requires some knowledge of the stereotype about mechanics being nitpicky.\n\nOverall, the joke is light-hearted and humorous, but it may not be the most memorable or impactful joke due to its reliance on a common stereotype. It could be improved by adding a more unexpected or unique twist to the punchline.'
```

In [ ]:
Copied!
```
for run_id, ckpts in wflow_ckptr.checkpoints.items():
    print(
        f"Run: {run_id} has stored checkpoints for steps {[c.last_completed_step for c in ckpts]}"
    )

```

for run_id, ckpts in wflow_ckptr.checkpoints.items(): print( f"Run: {run_id} has stored checkpoints for steps {[c.last_completed_step for c in ckpts]}" )
```
Run: 483eccdd-a035-42cc-b596-cd33d42938a7 has stored checkpoints for steps ['generate_joke', 'critique_joke']
Run: e112bca9-637c-4492-a8aa-926c302c99d4 has stored checkpoints for steps ['generate_joke', 'critique_joke']
Run: 7a59c918-90a3-47f8-a818-71e45897ae39 has stored checkpoints for steps ['generate_joke', 'critique_joke']
Run: 9dccfda3-b5bf-4771-8293-efd3e3a275a6 has stored checkpoints for steps ['critique_joke']
Run: 6390e2ce-63f4-44a3-8a75-64ccb765abfd has stored checkpoints for steps ['generate_joke']
Run: e3291623-6eb8-43c6-b102-dc6f88a42f4d has stored checkpoints for steps ['generate_joke', 'critique_joke']

```

