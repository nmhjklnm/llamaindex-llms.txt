# Llama Pack - Resume Screener 📄¶
![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
This example shows you how to use the Resume Screener Llama Pack. You can find all packs on https://llamahub.ai
The resume screener is designed to analyze a candidate's resume according to a set of criteria, and decide whether the candidate is a fit for the job.
in this example we'll evaluate a sample resume (e.g. Jerry's old resume).
In [ ]:
Copied!
```
%pip install llama-index-readers-wikipedia

```

%pip install llama-index-readers-wikipedia
In [ ]:
Copied!
```
!pip install llama-index llama-hub

```

!pip install llama-index llama-hub
### Setup Data¶
We'll load some sample Wikipedia data for OpenAI, Sam, Mira, and Emmett. Why? No reason in particular :)
In [ ]:
Copied!
```
from llama_index.readers.wikipedia import WikipediaReader

loader = WikipediaReader()
documents = loader.load_data(
    pages=["OpenAI", "Sam Altman", "Mira Murati", "Emmett Shear"],
    auto_suggest=False,
)

```

from llama_index.readers.wikipedia import WikipediaReader loader = WikipediaReader() documents = loader.load_data( pages=["OpenAI", "Sam Altman", "Mira Murati", "Emmett Shear"], auto_suggest=False, )
In [ ]:
Copied!
```
# do sentence splitting on the first piece of text
from llama_index.core.node_parser import SentenceSplitter

```

# do sentence splitting on the first piece of text from llama_index.core.node_parser import SentenceSplitter
In [ ]:
Copied!
```
sentence_splitter = SentenceSplitter(chunk_size=1024)

```

sentence_splitter = SentenceSplitter(chunk_size=1024)
We get the first chunk from each essay.
In [ ]:
Copied!
```
# get the first 1024 tokens for each entity
openai_node = sentence_splitter.get_nodes_from_documents([documents[0]])[0]
sama_node = sentence_splitter.get_nodes_from_documents([documents[1]])[0]
mira_node = sentence_splitter.get_nodes_from_documents([documents[2]])[0]
emmett_node = sentence_splitter.get_nodes_from_documents([documents[3]])[0]

```

# get the first 1024 tokens for each entity openai_node = sentence_splitter.get_nodes_from_documents([documents[0]])[0] sama_node = sentence_splitter.get_nodes_from_documents([documents[1]])[0] mira_node = sentence_splitter.get_nodes_from_documents([documents[2]])[0] emmett_node = sentence_splitter.get_nodes_from_documents([documents[3]])[0]
We'll also download Jerry's resume in 2019.
## Download Resume Screener Pack from LlamaHub¶
Here we download the resume screener pack class from LlamaHub.
We'll use it for two use cases:
  * whether the candidate is a good fit for a front-end / full-stack engineering role.
  * whether the candidate is a good fit for the CEO of OpenAI.


In [ ]:
Copied!
```
from llama_index.core.llama_pack import download_llama_pack

```

from llama_index.core.llama_pack import download_llama_pack
In [ ]:
Copied!
```
ResumeScreenerPack = download_llama_pack(
    "ResumeScreenerPack", "./resume_screener_pack"
)

```

ResumeScreenerPack = download_llama_pack( "ResumeScreenerPack", "./resume_screener_pack" )
### Screen Candidate for MLE Role¶
We take a job description on an MLE role from Meta's website.
In [ ]:
Copied!
```
meta_jd = """\
Meta is embarking on the most transformative change to its business and technology in company history, and our Machine Learning Engineers are at the forefront of this evolution. By leading crucial projects and initiatives that have never been done before, you have an opportunity to help us advance the way people connect around the world.
 
The ideal candidate will have industry experience working on a range of recommendation, classification, and optimization problems. You will bring the ability to own the whole ML life cycle, define projects and drive excellence across teams. You will work alongside the world’s leading engineers and researchers to solve some of the most exciting and massive social data and prediction problems that exist on the web.\
"""

```

meta_jd = """\ Meta is embarking on the most transformative change to its business and technology in company history, and our Machine Learning Engineers are at the forefront of this evolution. By leading crucial projects and initiatives that have never been done before, you have an opportunity to help us advance the way people connect around the world. The ideal candidate will have industry experience working on a range of recommendation, classification, and optimization problems. You will bring the ability to own the whole ML life cycle, define projects and drive excellence across teams. You will work alongside the world’s leading engineers and researchers to solve some of the most exciting and massive social data and prediction problems that exist on the web.\ """
In [ ]:
Copied!
```
resume_screener = ResumeScreenerPack(
    job_description=meta_jd,
    criteria=[
        "2+ years of experience in one or more of the following areas: machine learning, recommendation systems, pattern recognition, data mining, artificial intelligence, or related technical field",
        "Experience demonstrating technical leadership working with teams, owning projects, defining and setting technical direction for projects",
        "Bachelor's degree in Computer Science, Computer Engineering, relevant technical field, or equivalent practical experience.",
    ],
)

```

resume_screener = ResumeScreenerPack( job_description=meta_jd, criteria=[ "2+ years of experience in one or more of the following areas: machine learning, recommendation systems, pattern recognition, data mining, artificial intelligence, or related technical field", "Experience demonstrating technical leadership working with teams, owning projects, defining and setting technical direction for projects", "Bachelor's degree in Computer Science, Computer Engineering, relevant technical field, or equivalent practical experience.", ], )
In [ ]:
Copied!
```
response = resume_screener.run(resume_path="jerry_resume.pdf")

```

response = resume_screener.run(resume_path="jerry_resume.pdf")
In [ ]:
Copied!
```
for cd in response.criteria_decisions:
    print("### CRITERIA DECISION")
    print(cd.reasoning)
    print(cd.decision)
print("#### OVERALL REASONING ##### ")
print(str(response.overall_reasoning))
print(str(response.overall_decision))

```

for cd in response.criteria_decisions: print("### CRITERIA DECISION") print(cd.reasoning) print(cd.decision) print("#### OVERALL REASONING ##### ") print(str(response.overall_reasoning)) print(str(response.overall_decision))
```
### CRITERIA DECISION
Jerry Liu has more than 2 years of experience in machine learning and artificial intelligence. He worked as a Machine Learning Engineer at Quora Inc. for a year and has been an AI Research Scientist at Uber ATG since 2018. His work involves deep learning, information theory, and 3D geometry, among other areas.
True
### CRITERIA DECISION
Jerry Liu has demonstrated technical leadership in his roles at Uber ATG and Quora Inc. He has led and mentored multiple projects on multi-agent simulation, prediction, and planning. He also researched and productionized GBDT’s for new users at Quora, contributing to a 5% increase in new user active usage.
True
### CRITERIA DECISION
Jerry Liu has a Bachelor of Science in Engineering (B.S.E.) in Computer Science from Princeton University. He graduated Summa Cum Laude and was a member of Phi Beta Kappa, Tau Beta Pi, and Sigma Xi.
True
#### OVERALL REASONING ##### 
Jerry Liu meets all the screening criteria for the Machine Learning Engineer position at Meta. He has the required experience in machine learning and artificial intelligence, has demonstrated technical leadership, and has a relevant degree.
True

```

### Screen Candidate for FE / Typescript roles¶
In [ ]:
Copied!
```
resume_screener = ResumeScreenerPack(
    job_description="We're looking to hire a front-end engineer",
    criteria=[
        "The individual needs to be experienced in front-end / React / Typescript"
    ],
)

```

resume_screener = ResumeScreenerPack( job_description="We're looking to hire a front-end engineer", criteria=[ "The individual needs to be experienced in front-end / React / Typescript" ], )
In [ ]:
Copied!
```
response = resume_screener.run(resume_path="jerry_resume.pdf")

```

response = resume_screener.run(resume_path="jerry_resume.pdf")
In [ ]:
Copied!
```
print(str(response.overall_reasoning))
print(str(response.overall_decision))

```

print(str(response.overall_reasoning)) print(str(response.overall_decision))
```
The candidate does not meet the specific criteria of having experience in front-end, React, or Typescript.
False

```

### Screen Candidate for CEO of OpenAI¶
Jerry can't write Typescript, but can he be CEO of OpenAI?
In [ ]:
Copied!
```
job_description = f"""\
We're looking to hire a CEO for OpenAI.

Instead of listing a set of specific criteria, each "criteria" is instead a short biography of a previous CEO.\

For each criteria/bio, outline if the candidate's experience matches or surpasses that of the candidate.

Also, here's a description of OpenAI from Wikipedia: 
{openai_node.get_content()}
"""

profile_strs = [
    f"Profile: {n.get_content()}" for n in [sama_node, mira_node, emmett_node]
]


resume_screener = ResumeScreenerPack(
    job_description=job_description, criteria=profile_strs
)

```

job_description = f"""\ We're looking to hire a CEO for OpenAI. Instead of listing a set of specific criteria, each "criteria" is instead a short biography of a previous CEO.\ For each criteria/bio, outline if the candidate's experience matches or surpasses that of the candidate. Also, here's a description of OpenAI from Wikipedia: {openai_node.get_content()} """ profile_strs = [ f"Profile: {n.get_content()}" for n in [sama_node, mira_node, emmett_node] ] resume_screener = ResumeScreenerPack( job_description=job_description, criteria=profile_strs )
In [ ]:
Copied!
```
response = resume_screener.run(resume_path="jerry_resume.pdf")

```

response = resume_screener.run(resume_path="jerry_resume.pdf")
In [ ]:
Copied!
```
for cd in response.criteria_decisions:
    print("### CRITERIA DECISION")
    print(cd.reasoning)
    print(cd.decision)
print("#### OVERALL REASONING ##### ")
print(str(response.overall_reasoning))
print(str(response.overall_decision))

```

for cd in response.criteria_decisions: print("### CRITERIA DECISION") print(cd.reasoning) print(cd.decision) print("#### OVERALL REASONING ##### ") print(str(response.overall_reasoning)) print(str(response.overall_decision))
```
### CRITERIA DECISION
The candidate, Jerry Liu, has a strong background in AI research and has led multiple projects in this field. However, he does not have the same level of executive leadership experience as Samuel Harris Altman, who served as CEO of OpenAI and president of Y Combinator. Altman also has experience leading an advanced AI research team at Microsoft, which Liu does not have.
False
### CRITERIA DECISION
While Jerry Liu has a strong background in AI and machine learning, his experience does not match or surpass that of Mira Murati. Murati served as the chief technology officer of OpenAI and briefly as its interim CEO. She led the company's work on several major projects and oversaw multiple teams. Liu does not have the same level of leadership or executive experience.
False
### CRITERIA DECISION
Jerry Liu's experience does not match or surpass that of Emmett Shear. Shear co-founded Justin.tv and served as the CEO of Twitch, demonstrating significant entrepreneurial and executive leadership experience. He also served as a part-time partner at venture capital firm Y Combinator and briefly as interim CEO of OpenAI. Liu, while having a strong background in AI research, does not have the same level of leadership or executive experience.
False
#### OVERALL REASONING ##### 
While Jerry Liu has a strong background in AI research and has led multiple projects in this field, his experience does not match or surpass that of the previous CEOs in terms of executive leadership and entrepreneurial experience.
False

```

...sadly not
