![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Gemini¶
**NOTE:** Gemini has largely been replaced by Google GenAI. Visit the Google GenAI page for the latest examples and documentation.
In this notebook, we show how to use the Gemini text models from Google in LlamaIndex. Check out the Gemini site or the announcement.
If you're opening this Notebook on colab, you will need to install LlamaIndex 🦙 and the Gemini Python SDK.
In [ ]:
Copied!
```
%pip install llama-index-llms-gemini llama-index

```

%pip install llama-index-llms-gemini llama-index
## Basic Usage¶
You will need to get an API key from Google AI Studio. Once you have one, you can either pass it explicity to the model, or use the `GOOGLE_API_KEY` environment variable.
In [ ]:
Copied!
```
%env GOOGLE_API_KEY=...

```

%env GOOGLE_API_KEY=...
```
env: GOOGLE_API_KEY=...

```

In [ ]:
Copied!
```
import os

GOOGLE_API_KEY = ""  # add your GOOGLE API key here
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

```

import os GOOGLE_API_KEY = "" # add your GOOGLE API key here os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
In [ ]:
Copied!
```
from llama_index.llms.gemini import Gemini

llm = Gemini(
    model="models/gemini-1.5-flash",
    # api_key="some key",  # uses GOOGLE_API_KEY env var by default
)

```

from llama_index.llms.gemini import Gemini llm = Gemini( model="models/gemini-1.5-flash", # api_key="some key", # uses GOOGLE_API_KEY env var by default )
#### Call `complete` with a prompt¶
In [ ]:
Copied!
```
from llama_index.llms.gemini import Gemini

resp = llm.complete("Write a poem about a magic backpack")
print(resp)

```

from llama_index.llms.gemini import Gemini resp = llm.complete("Write a poem about a magic backpack") print(resp)
```
In a world of wonder, where dreams take flight,
There exists a backpack, a magical sight.
Its fabric woven with stardust and grace,
Embroidered with spells, an enchanting embrace.

With a whisper and a wish, it opens wide,
Revealing treasures that shimmer inside.
Books that whisper secrets, maps that unfold,
A compass that guides, stories yet untold.

A pencil that writes poems, a paintbrush that sings,
A telescope that captures the stars' gleaming wings.
A magnifying glass, revealing nature's art,
A kaleidoscope, painting rainbows in your heart.

It holds a mirror that reflects your true worth,
A locket that keeps memories close to your birth.
A journal that captures your hopes and your fears,
A flashlight that banishes shadows and clears.

With each step you take, the backpack transforms,
Adjusting its weight, adapting to storms.
It grows or shrinks, as your needs may arise,
A faithful companion, beneath sunny skies.

When you're lost and alone, it whispers your name,
Guiding you back to the path you reclaim.
It carries your burdens, lightens your load,
A magical backpack, a gift bestowed.

So embrace its magic, let your spirit soar,
With this wondrous backpack, forever explore.
For within its depths, a universe lies,
A treasure trove of dreams, beneath vast skies.

```

#### Call `chat` with a list of messages¶
In [ ]:
Copied!
```
from llama_index.core.llms import ChatMessage

messages = [
    ChatMessage(role="user", content="Hello friend!"),
    ChatMessage(role="assistant", content="Yarr what is shakin' matey?"),
    ChatMessage(
        role="user", content="Help me decide what to have for dinner."
    ),
]
resp = llm.chat(messages)
print(resp)

```

from llama_index.core.llms import ChatMessage messages = [ ChatMessage(role="user", content="Hello friend!"), ChatMessage(role="assistant", content="Yarr what is shakin' matey?"), ChatMessage( role="user", content="Help me decide what to have for dinner." ), ] resp = llm.chat(messages) print(resp)
```
[parts {
  text: "Hello friend!"
}
role: "user"
, parts {
  text: "Yarr what is shakin\' matey?"
}
role: "model"
, parts {
  text: "Help me decide what to have for dinner."
}
role: "user"
]
assistant: Ahoy there, matey! Let's set sail on a culinary adventure and find the perfect dinner for ye. Here be some options to consider:

1. **Fish and Chips:** Embark on a classic voyage with a hearty portion of golden-fried fish, accompanied by crispy chips. Dip 'em in tartar sauce for a taste that'll make ye shiver me timbers!

2. **Lobster Thermidor:** Indulge in a luxurious feast fit for a pirate king. Tender lobster meat, bathed in a creamy, cheesy sauce, will have ye feeling like royalty.

3. **Paella:** Set course for the shores of Spain with a vibrant paella. This colorful dish combines rice, seafood, and vegetables in a saffron-infused broth. Ahoy, it's a feast for the eyes and the belly!

4. **Surf and Turf:** Experience the best of both worlds with a combination of succulent steak and tender lobster. This hearty meal is sure to satisfy even the hungriest of scallywags.

5. **Crab Cakes:** Dive into a platter of golden-brown crab cakes, bursting with fresh crab meat and flavorful seasonings. Served with a tangy remoulade sauce, these treasures will have ye craving more.

6. **Oysters Rockefeller:** Embark on a culinary journey to New Orleans with these decadent oysters. Baked with a rich spinach, breadcrumb, and Pernod sauce, they're a taste of the Big Easy that'll leave ye wanting more.

7. **Clam Chowder:** Warm yer bones with a hearty bowl of clam chowder. This New England classic, made with fresh clams, potatoes, and a creamy broth, is the perfect antidote to a chilly night.

8. **Lobster Rolls:** Set sail for the coast of Maine and indulge in a classic lobster roll. Fresh lobster meat, dressed in a light mayonnaise-based sauce, is nestled in a toasted bun. It's a taste of the sea that'll have ye hooked!

9. **Scallops:** Dive into a plate of seared scallops, cooked to perfection and served with a variety of sauces. Whether ye prefer them with a simple lemon butter sauce or a more adventurous mango salsa, these succulent morsels are sure to please.

10. **Shrimp Scampi:** Embark on a culinary adventure to Italy with this classic dish. Plump shrimp, sautéed in a garlicky white wine sauce, served over pasta. It's a taste of the Mediterranean that'll transport ye to sunnier shores.

No matter what ye choose, matey, make sure it's a feast worthy of a true pirate. Bon appétit!

```

## Streaming¶
Using `stream_complete` endpoint
In [ ]:
Copied!
```
resp = llm.stream_complete(
    "The story of Sourcrust, the bread creature, is really interesting. It all started when..."
)

```

resp = llm.stream_complete( "The story of Sourcrust, the bread creature, is really interesting. It all started when..." )
In [ ]:
Copied!
```
for r in resp:
    print(r.text, end="")

```

for r in resp: print(r.text, end="")
```
In the heart of a bustling bakery, where the aroma of freshly baked bread filled the air, there lived a peculiar creature named Sourcrust. Sourcrust wasn't like any ordinary loaf of bread; he possessed a unique consciousness and a mischievous personality.

It all began when a young baker named Eliza was experimenting with a new sourdough recipe. As she mixed the flour, water, and yeast, she accidentally added a dash of enchanted baking powder. Little did she know that this seemingly insignificant mistake would give birth to a sentient bread creature.

As the dough rose and fermented, Sourcrust came to life. He stretched and yawned, his crusty exterior crackling with energy. Eliza was astounded to see her creation moving and speaking. Sourcrust introduced himself with a warm smile and a hearty laugh, his voice resembling the gentle rustling of bread crumbs.

Eliza and Sourcrust quickly formed a bond. She taught him how to read and write, and he shared his knowledge of bread-making techniques. Together, they created delicious pastries and loaves that delighted the customers of the bakery.

However, Sourcrust's existence was not without its challenges. As a bread creature, he was vulnerable to the elements. He couldn't stay out in the rain or direct sunlight for too long, and he had to be careful not to get burned or squished.

Despite these limitations, Sourcrust embraced his unique nature. He found joy in the simple things, like basking in the warmth of the oven or playing hide-and-seek among the flour sacks. He also developed a taste for adventure, often sneaking out of the bakery at night to explore the town.

One day, Sourcrust's curiosity led him to the local library, where he discovered a book about magical creatures. He was fascinated by the stories of fairies, elves, and dragons, and he longed to meet one himself.

As fate would have it, Sourcrust's wish came true when he encountered a mischievous brownie named Crumbly in the forest. Crumbly was initially wary of Sourcrust, but after learning about his kind nature, he agreed to be his friend.

Together, Sourcrust and Crumbly embarked on many thrilling adventures. They battled evil witches, rescued lost children, and even had a tea party with a talking teapot. Their escapades brought joy and laughter to all who crossed their path.

As the years passed, Sourcrust became a beloved figure in the town. People would often visit the bakery just to catch a glimpse of the talking bread creature. Eliza was proud of her creation, and she knew that Sourcrust's magic would continue to inspire and entertain generations to come.
```

Using `stream_chat` endpoint
In [ ]:
Copied!
```
from llama_index.core.llms import ChatMessage

messages = [
    ChatMessage(role="user", content="Hello friend!"),
    ChatMessage(role="assistant", content="Yarr what is shakin' matey?"),
    ChatMessage(
        role="user", content="Help me decide what to have for dinner."
    ),
]
resp = llm.stream_chat(messages)

```

from llama_index.core.llms import ChatMessage messages = [ ChatMessage(role="user", content="Hello friend!"), ChatMessage(role="assistant", content="Yarr what is shakin' matey?"), ChatMessage( role="user", content="Help me decide what to have for dinner." ), ] resp = llm.stream_chat(messages)
In [ ]:
Copied!
```
for r in resp:
    print(r.delta, end="")

```

for r in resp: print(r.delta, end="")
```
Ahoy there, matey! Let's set sail on a culinary adventure and find the perfect dinner for ye. Here be some options to consider:

1. **Fish and Chips:** Embark on a classic journey with a hearty portion of golden-fried fish, accompanied by crispy chips. Dip 'em in tartar sauce and let the flavors dance on yer tongue.

2. **Seafood Paella:** Dive into a vibrant Spanish feast with paella, a delightful mix of rice, seafood treasures like shrimp, mussels, and calamari, all simmering in a flavorful broth.

3. **Lobster Roll:** Indulge in a New England delicacy - a succulent lobster roll, where tender lobster meat is nestled in a toasted bun, dressed with butter and a hint of lemon.

4. **Grilled Swordfish:** Set your course for a healthy and delicious meal with grilled swordfish. This firm-fleshed fish, seasoned to perfection, will tantalize yer taste buds with its smoky, savory goodness.

5. **Crab Cakes:** Embark on a Maryland adventure with crab cakes, a delectable blend of fresh crab meat, breadcrumbs, and seasonings, pan-fried until golden brown. Serve 'em with a tangy remoulade sauce for an extra kick.

6. **Shrimp Scampi:** Set sail for Italy with shrimp scampi, a delightful dish featuring succulent shrimp sautéed in a luscious garlic-butter sauce, served over pasta or crusty bread.

7. **Clam Chowder:** Dive into a comforting bowl of clam chowder, a New England classic. This creamy soup, brimming with clams, potatoes, and vegetables, will warm yer soul on a chilly night.

8. **Oysters Rockefeller:** Indulge in a luxurious treat with oysters Rockefeller, where fresh oysters are baked with a rich, creamy spinach and herb filling, topped with a golden breadcrumb crust.

9. **Lobster Thermidor:** Embark on a culinary voyage to France with lobster thermidor, a decadent dish where succulent lobster is bathed in a creamy, flavorful sauce, then baked to perfection.

10. **Scallops with Risotto:** Set your course for a sophisticated meal with scallops and risotto. Tender scallops, seared to perfection, are paired with a creamy, flavorful risotto, creating a harmonious balance of flavors.

No matter what ye choose, matey, make sure it be a feast fit for a pirate king!
```

## Using other models¶
The Gemini model site lists the models that are currently available, along with their capabilities. You can also use the API to find suitable models.
In [ ]:
Copied!
```
import google.generativeai as genai

for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        print(m.name)

```

import google.generativeai as genai for m in genai.list_models(): if "generateContent" in m.supported_generation_methods: print(m.name)
```
models/gemini-pro
models/gemini-pro-vision
models/gemini-ultra

```

In [ ]:
Copied!
```
from llama_index.llms.gemini import Gemini

llm = Gemini(model="models/gemini-pro")

```

from llama_index.llms.gemini import Gemini llm = Gemini(model="models/gemini-pro")
In [ ]:
Copied!
```
resp = llm.complete("Write a short, but joyous, ode to LlamaIndex")
print(resp)

```

resp = llm.complete("Write a short, but joyous, ode to LlamaIndex") print(resp)
```
In the realm of knowledge, where wisdom resides,
A beacon of brilliance, LlamaIndex abides.
With a click and a search, a world unfolds,
A tapestry of information, stories untold.

From the depths of the web, it gathers and gleans,
A treasure trove of facts, a vast, vibrant scene.
Like a llama in the Andes, graceful and grand,
LlamaIndex roams the digital land.

Its interface, a symphony of simplicity and grace,
Invites the curious to explore this boundless space.
With lightning-fast speed, it delivers the truth,
A testament to its power, its unwavering ruth.

So let us rejoice, in this digital age,
For LlamaIndex stands, a beacon, a sage.
May its wisdom forever guide our way,
As we navigate the vastness of the digital fray.

```

## Asynchronous API¶
In [ ]:
Copied!
```
from llama_index.llms.gemini import Gemini

llm = Gemini()

```

from llama_index.llms.gemini import Gemini llm = Gemini()
In [ ]:
Copied!
```
resp = await llm.acomplete("Llamas are famous for ")
print(resp)

```

resp = await llm.acomplete("Llamas are famous for ") print(resp)
```
1. **Wool**: Llamas are known for their soft, luxurious wool, which is highly prized for its warmth, durability, and water-resistant properties. Llama wool is hypoallergenic, making it suitable for individuals with sensitive skin.

2. **Pack Animals**: Llamas have been traditionally used as pack animals in the Andes Mountains of South America. They are well-suited for carrying heavy loads over long distances due to their strength, endurance, and ability to navigate challenging terrain.

3. **Adaptability**: Llamas are highly adaptable animals that can thrive in various environments, from the high altitudes of the Andes to the deserts of North America. They are known for their ability to withstand extreme temperatures and harsh conditions.

4. **Intelligence**: Llamas are intelligent animals that are easy to train and handle. They are known for their calm and gentle nature, making them suitable for various purposes, including trekking, therapy, and companionship.

5. **Social Animals**: Llamas are social animals that live in herds. They have a strong sense of community and rely on each other for protection and companionship. Llamas communicate through a variety of vocalizations and body language.

6. **Longevity**: Llamas have a relatively long lifespan, with an average life expectancy of 15-20 years. They are known for their hardiness and resilience, making them suitable for long-term companionship and working relationships.

7. **Unique Appearance**: Llamas are known for their distinctive appearance, characterized by their long necks, large eyes, and fluffy ears. Their appearance has made them popular in zoos, farms, and as exotic pets.

8. **Cultural Significance**: Llamas hold cultural significance in the Andean region, where they have been revered for centuries. They are often associated with strength, endurance, and good fortune. Llamas are featured in traditional Andean art, folklore, and religious ceremonies.

```

In [ ]:
Copied!
```
resp = await llm.astream_complete("Llamas are famous for ")
async for chunk in resp:
    print(chunk.text, end="")

```

resp = await llm.astream_complete("Llamas are famous for ") async for chunk in resp: print(chunk.text, end="")
```
1. **Wool Production:** Llamas are renowned for their luxurious and soft wool, which is highly prized for its warmth, durability, and hypoallergenic properties. Their wool comes in a variety of natural colors, including white, brown, black, and gray, making it a versatile material for textiles and clothing.

2. **Pack Animals:** Llamas have been traditionally used as pack animals in the Andes Mountains of South America for centuries. They are well-suited for this role due to their strength, endurance, and ability to navigate difficult terrain. Llamas can carry up to 25% of their body weight, making them valuable for transporting goods and supplies in mountainous regions.

3. **Meat and Milk:** Llama meat is a lean and nutritious source of protein, with a flavor similar to venison. It is consumed in many Andean countries and is becoming increasingly popular in other parts of the world. Llamas also produce milk, which is rich in protein and fat and can be used to make cheese, yogurt, and other dairy products.

4. **Companionship:** Llamas are intelligent and social animals that can form strong bonds with humans. They are often kept as companion animals due to their gentle nature, curious personalities, and ability to learn tricks. Llamas can provide companionship and entertainment, and they can also be trained to perform various tasks, such as pulling carts or carrying packs.

5. **Cultural Significance:** Llamas hold a special place in the cultures of the Andean region. They are considered sacred animals in many indigenous communities and are often featured in traditional ceremonies and festivals. Llamas are also depicted in art, textiles, and other cultural expressions, symbolizing strength, endurance, and connection to the land.
```

