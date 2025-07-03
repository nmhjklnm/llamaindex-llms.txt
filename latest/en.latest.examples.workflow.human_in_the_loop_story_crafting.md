![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Choose Your Own Adventure Workflow (Human In The Loop)¶
For some Workflow applications, it may desirable and/or required to have humans involved in its execution. For example, a step of a Workflow may need human expertise or input in order to run. In another scenario, it may be required to have a human validate the initial output of a Workflow.
In this notebook, we show how one can implement a human-in-the-loop pattern with Workflows. Here we'll build a Workflow that creates stories in the style of Choose Your Own Adventure, where the LLM produces a segment of the story along with potential actions, and a human is required to choose from one of those actions.
## Generating Segments Of The Story With An LLM¶
Here, we'll make use of the ability to produce structured outputs from an LLM. We will task the LLM to create a segment of the story that is in continuation of previously generated segments and action choices.
In [ ]:
Copied!
```
from typing import Any, List

from llama_index.llms.openai import OpenAI
from llama_index.core.bridge.pydantic import BaseModel, Field
from llama_index.core.prompts import PromptTemplate

```

from typing import Any, List from llama_index.llms.openai import OpenAI from llama_index.core.bridge.pydantic import BaseModel, Field from llama_index.core.prompts import PromptTemplate
In [ ]:
Copied!
```
class Segment(BaseModel):
    """Data model for generating segments of a story."""

    plot: str = Field(
        description="The plot of the adventure for the current segment. The plot should be no longer than 3 sentences."
    )
    actions: List[str] = Field(
        default=[],
        description="The list of actions the protaganist can take that will shape the plot and actions of the next segment.",
    )

```

class Segment(BaseModel): """Data model for generating segments of a story.""" plot: str = Field( description="The plot of the adventure for the current segment. The plot should be no longer than 3 sentences." ) actions: List[str] = Field( default=[], description="The list of actions the protaganist can take that will shape the plot and actions of the next segment.", )
In [ ]:
Copied!
```
SEGMENT_GENERATION_TEMPLATE = """
You are working with a human to create a story in the style of choose your own adventure.

The human is playing the role of the protaganist in the story which you are tasked to
help write. To create the story, we do it in steps, where each step produces a BLOCK.
Each BLOCK consists of a PLOT, a set of ACTIONS that the protaganist can take, and the
chosen ACTION. 

Below we attach the history of the adventure so far.

PREVIOUS BLOCKS:
---
{running_story}

Continue the story by generating the next block's PLOT and set of ACTIONs. If there are
no previous BLOCKs, start an interesting brand new story. Give the protaganist a name and an
interesting challenge to solve.


Use the provided data model to structure your output.
"""

```

SEGMENT_GENERATION_TEMPLATE = """ You are working with a human to create a story in the style of choose your own adventure. The human is playing the role of the protaganist in the story which you are tasked to help write. To create the story, we do it in steps, where each step produces a BLOCK. Each BLOCK consists of a PLOT, a set of ACTIONS that the protaganist can take, and the chosen ACTION. Below we attach the history of the adventure so far. PREVIOUS BLOCKS: --- {running_story} Continue the story by generating the next block's PLOT and set of ACTIONs. If there are no previous BLOCKs, start an interesting brand new story. Give the protaganist a name and an interesting challenge to solve. Use the provided data model to structure your output. """
In [ ]:
Copied!
```
FINAL_SEGMENT_GENERATION_TEMPLATE = """
You are working with a human to create a story in the style of choose your own adventure.

The human is playing the role of the protaganist in the story which you are tasked to
help write. To create the story, we do it in steps, where each step produces a BLOCK.
Each BLOCK consists of a PLOT, a set of ACTIONS that the protaganist can take, and the
chosen ACTION. Below we attach the history of the adventure so far.

PREVIOUS BLOCKS:
---
{running_story}

The story is now coming to an end. With the previous blocks, wrap up the story with a
closing PLOT. Since it is a closing plot, DO NOT GENERATE a new set of actions.

Use the provided data model to structure your output.
"""

```

FINAL_SEGMENT_GENERATION_TEMPLATE = """ You are working with a human to create a story in the style of choose your own adventure. The human is playing the role of the protaganist in the story which you are tasked to help write. To create the story, we do it in steps, where each step produces a BLOCK. Each BLOCK consists of a PLOT, a set of ACTIONS that the protaganist can take, and the chosen ACTION. Below we attach the history of the adventure so far. PREVIOUS BLOCKS: --- {running_story} The story is now coming to an end. With the previous blocks, wrap up the story with a closing PLOT. Since it is a closing plot, DO NOT GENERATE a new set of actions. Use the provided data model to structure your output. """
In [ ]:
Copied!
```
# Let's see an example segment
llm = OpenAI("gpt-4o")
segment = llm.structured_predict(
    Segment,
    PromptTemplate(SEGMENT_GENERATION_TEMPLATE),
    running_story="",
)

```

# Let's see an example segment llm = OpenAI("gpt-4o") segment = llm.structured_predict( Segment, PromptTemplate(SEGMENT_GENERATION_TEMPLATE), running_story="", )
In [ ]:
Copied!
```
segment

```

segment
Out[ ]:
```
Segment(plot="In the bustling city of Eldoria, a young adventurer named Aric discovered a mysterious map hidden inside an old bookshop. The map hinted at a hidden treasure buried deep within the enchanted Whispering Woods. Intrigued and eager for adventure, Aric decided to follow the map's clues.", actions=['Follow the map to the Whispering Woods', 'Seek advice from the old bookshop owner', 'Gather supplies for the journey', 'Ignore the map and continue with daily life'])
```

### Stitching together previous segments¶
We need to stich together story segments and pass this in to the prompt as the value for `running_story`. We define a `Block` data class that holds the `Segment` as well as the `choice` of action.
In [ ]:
Copied!
```
import uuid
from typing import Optional

BLOCK_TEMPLATE = """
BLOCK
===
PLOT: {plot}
ACTIONS: {actions}
CHOICE: {choice}
"""


class Block(BaseModel):
    id_: str = Field(default_factory=lambda: str(uuid.uuid4()))
    segment: Segment
    choice: Optional[str] = None
    block_template: str = BLOCK_TEMPLATE

    def __str__(self):
        return self.block_template.format(
            plot=self.segment.plot,
            actions=", ".join(self.segment.actions),
            choice=self.choice or "",
        )

```

import uuid from typing import Optional BLOCK_TEMPLATE = """ BLOCK === PLOT: {plot} ACTIONS: {actions} CHOICE: {choice} """ class Block(BaseModel): id_: str = Field(default_factory=lambda: str(uuid.uuid4())) segment: Segment choice: Optional[str] = None block_template: str = BLOCK_TEMPLATE def __str__(self): return self.block_template.format( plot=self.segment.plot, actions=", ".join(self.segment.actions), choice=self.choice or "", )
In [ ]:
Copied!
```
block = Block(segment=segment)
print(block)

```

block = Block(segment=segment) print(block)
```
BLOCK
===
PLOT: In the bustling city of Eldoria, a young adventurer named Aric discovered a mysterious map hidden inside an old bookshop. The map hinted at a hidden treasure buried deep within the enchanted Whispering Woods. Intrigued and eager for adventure, Aric decided to follow the map's clues.
ACTIONS: Follow the map to the Whispering Woods, Seek advice from the old bookshop owner, Gather supplies for the journey, Ignore the map and continue with daily life
CHOICE: 


```

## Create The Choose Your Own Adventure Workflow¶
This Workflow will consist of two steps that will cycle until a max number of steps (i.e., segments) has been produced. The first step will have the LLM create a new `Segment`, which will be used to create a new story `Block`. The second step will prompt the human to choose their adventure from the list of actions specified in the newly created `Segment`.
In [ ]:
Copied!
```
from llama_index.core.workflow import (
    Context,
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)

```

from llama_index.core.workflow import ( Context, Event, StartEvent, StopEvent, Workflow, step, )
In [ ]:
Copied!
```
class NewBlockEvent(Event):
    block: Block


class HumanChoiceEvent(Event):
    block_id: str

```

class NewBlockEvent(Event): block: Block class HumanChoiceEvent(Event): block_id: str
In [ ]:
Copied!
```
class ChooseYourOwnAdventureWorkflow(Workflow):
    def __init__(self, max_steps: int = 3, **kwargs):
        super().__init__(**kwargs)
        self.llm = OpenAI("gpt-4o")
        self.max_steps = max_steps

    @step
    async def create_segment(
        self, ctx: Context, ev: StartEvent | HumanChoiceEvent
    ) -> NewBlockEvent | StopEvent:
        blocks = await ctx.store.get("blocks", [])
        running_story = "\n".join(str(b) for b in blocks)

        if len(blocks) < self.max_steps:
            new_segment = self.llm.structured_predict(
                Segment,
                PromptTemplate(SEGMENT_GENERATION_TEMPLATE),
                running_story=running_story,
            )
            new_block = Block(segment=new_segment)
            blocks.append(new_block)
            await ctx.store.set("blocks", blocks)
            return NewBlockEvent(block=new_block)
        else:
            final_segment = self.llm.structured_predict(
                Segment,
                PromptTemplate(FINAL_SEGMENT_GENERATION_TEMPLATE),
                running_story=running_story,
            )
            final_block = Block(segment=final_segment)
            blocks.append(final_block)
            return StopEvent(result=blocks)

    @step
    async def prompt_human(
        self, ctx: Context, ev: NewBlockEvent
    ) -> HumanChoiceEvent:
        block = ev.block

        # get human input
        human_prompt = f"\n===\n{ev.block.segment.plot}\n\n"
        human_prompt += "Choose your adventure:\n\n"
        human_prompt += "\n".join(ev.block.segment.actions)
        human_prompt += "\n\n"
        human_input = input(human_prompt)

        blocks = await ctx.store.get("blocks")
        block.choice = human_input
        blocks[-1] = block
        await ctx.store.set("block", blocks)

        return HumanChoiceEvent(block_id=ev.block.id_)

```

class ChooseYourOwnAdventureWorkflow(Workflow): def __init__(self, max_steps: int = 3, **kwargs): super().__init__(**kwargs) self.llm = OpenAI("gpt-4o") self.max_steps = max_steps @step async def create_segment( self, ctx: Context, ev: StartEvent | HumanChoiceEvent ) -> NewBlockEvent | StopEvent: blocks = await ctx.store.get("blocks", []) running_story = "\n".join(str(b) for b in blocks) if len(blocks) < self.max_steps: new_segment = self.llm.structured_predict( Segment, PromptTemplate(SEGMENT_GENERATION_TEMPLATE), running_story=running_story, ) new_block = Block(segment=new_segment) blocks.append(new_block) await ctx.store.set("blocks", blocks) return NewBlockEvent(block=new_block) else: final_segment = self.llm.structured_predict( Segment, PromptTemplate(FINAL_SEGMENT_GENERATION_TEMPLATE), running_story=running_story, ) final_block = Block(segment=final_segment) blocks.append(final_block) return StopEvent(result=blocks) @step async def prompt_human( self, ctx: Context, ev: NewBlockEvent ) -> HumanChoiceEvent: block = ev.block # get human input human_prompt = f"\n===\n{ev.block.segment.plot}\n\n" human_prompt += "Choose your adventure:\n\n" human_prompt += "\n".join(ev.block.segment.actions) human_prompt += "\n\n" human_input = input(human_prompt) blocks = await ctx.store.get("blocks") block.choice = human_input blocks[-1] = block await ctx.store.set("block", blocks) return HumanChoiceEvent(block_id=ev.block.id_)
### Running The Workflow¶
Since workflows are async first, this all runs fine in a notebook. If you were running in your own code, you would want to use `asyncio.run()` to start an async event loop if one isn't already running.
```
async def main():
    <async code>

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

```

In [ ]:
Copied!
```
import nest_asyncio

nest_asyncio.apply()

```

import nest_asyncio nest_asyncio.apply()
In [ ]:
Copied!
```
w = ChooseYourOwnAdventureWorkflow(timeout=None)

```

w = ChooseYourOwnAdventureWorkflow(timeout=None)
In [ ]:
Copied!
```
result = await w.run()

```

result = await w.run()
### Print The Final Story¶
In [ ]:
Copied!
```
final_story = "\n\n".join(b.segment.plot for b in result)
print(final_story)

```

final_story = "\n\n".join(b.segment.plot for b in result) print(final_story)
```
In the bustling city of Eldoria, a young adventurer named Aric discovered a mysterious map hidden in an old bookshop. The map hinted at a hidden treasure buried deep within the Whispering Woods, a place known for its eerie silence and ancient secrets. Determined to uncover the treasure, Aric set off on his journey, leaving the city behind.

Aric found a seasoned guide named Elara, who knew the Whispering Woods like the back of her hand. Elara agreed to help Aric, intrigued by the promise of hidden treasure. Together, they ventured into the forest, the map leading them to a fork in the path where the trees seemed to whisper secrets.

Elara examined the map closely and listened to the whispers of the trees. She suggested taking the left path, as it seemed to align with the ancient markings on the map. Trusting her expertise, Aric and Elara proceeded down the left path, where the forest grew denser and the air filled with an eerie stillness.

As Aric and Elara searched for hidden clues along the dense path, they stumbled upon an ancient stone altar covered in moss and vines. Upon closer inspection, they discovered a hidden compartment within the altar containing the long-lost treasure—a chest filled with gold, jewels, and ancient artifacts. With their mission complete, Aric and Elara returned to Eldoria, their bond strengthened by the adventure and their hearts filled with the thrill of discovery.

```

### Other Ways To Implement Human In The Loop¶
One could also implement the human in the loop by creating a separate Workflow just for gathering human input and making use of nested Workflows. This design could be used in situations where you would want the human input gathering to be a separate service from the rest of the Workflow, which is what would happen if you deployed the nested workflows with llama-deploy.
