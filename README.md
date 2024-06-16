# EHRmonize

Welcome to `ehrmonize`, an AI-powered Python package to automatically clean and categorize medical concepts when doing EHR data science. 

## User Story
> As a data scientist working with EHR data, I want to be able to automatically categorize concepts so that I don't need to annoy my clinician friends (as much).


## Current supported models / engines / APIs

| API           | model_id                              |
|---------------|---------------------------------------|
| OpenAI        | gpt-3.5-turbo                         |
|               | gpt-4                                 |
|               | gpt-4o                                |
| AWS Bedrock   | anthropic.claude-instant-v1           |
|               | anthropic.claude-v2:1                 |
|               | meta.llama2-13b-chat-v1               |
|               | meta.llama2-70b-chat-v1               |
|               | meta.llama3-70b-instruct-v1:0         |
|               | mistral.mistral-7b-instruct-v0:2      |
|               | mistral.mixtral-8x7b-instruct-v0:1    |
