# chat311

311 service request generation using OpenAI

## Quick Start

Install dependencies:

```bash
pip install -r requirements
```

Configure your OpenAI API key:

```bash
export OPENAI_API_KEY="sk-************************************************"
```

Launch the Streamlit app:

```bash
streamlit run chat311.py
```

## Guiding purpose
As ChatGPT has gone viral, the potential for government use cases are sure to be brainstormed as well. While there are many questions about the efficacy of ChatGPT and OpenAI, there is potential for improving service delivery and providing easier ways for residents to interact with their government.

A key way residents and local governments interact is via a 311 request process. It is the way people can inform a city that a pothole is present on a road, a water main has broken, or a water main has broken.

There are several issues with 311 systems:
- many are staffed with employees that only work from 9-5 - not always convenient when resident may only have time to make a request during non-typical work hours
- the categories of request are created to sync with the way city departments work, not with how residents think of their city. For instance, a hole in the road could be a pothole or it could be a sunken manhole cover. The resolution to that specific issue might be  owned by different departments. 311 systems often require the requester know the difference.
- because of the broad number of service request categories, it is hard to compare city-to-city to set baselines and learn best practices about resolving issues

Our plan:
As a proof of concept, we plan to determine how OpenAI's APIs could help resolve these issues:
- categorize service requests automatically
- compare service requests across cities to set baselines
