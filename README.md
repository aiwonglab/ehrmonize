# EHRmonize

Welcome to `EHRmonize`, a Python package to abstract medical concepts using large language models.

## Citation

> TBD, stay tuned!


## Motivation
Processing and harmonizing the vast amounts of data captured in complex electronic health records (EHR) is a challenging and costly task that requires clinical expertise. Large language models (LLMs) have shown promise in various healthcare-related tasks. We herein introduce `EHRmonize`, a framework designed to abstract EHR medical concepts using LLMs.

## Rationale
`EHRmonize` is designed with two main components: a corpus generation and an LLM inference pipeline. The **first step** entails querying the EHR databases to extract and the text/concepts across various data domains that need categorization. The **second step** employs LLM few-shot prompting across different tasks. The objective is to leverage the vast medical text exposure of LLMs to convert raw input medication data into useful, predefined classes.


## Current supported tasks

| Type          | Task                          |
|---------------|-------------------------------|
| Free-text     | *get_generic_name*            |
|               | *get_generic_route*           |
| Multiclass    | *classify_drug*               |
| Binary        | *one_hot_drug_classification* |
| Custom        | *custom*                      |


## Current supported models / engines / APIs

| API           | model_id                                      |
|---------------|-----------------------------------------------|
| OpenAI        | gpt-4                                         |
|               | gpt-4o                                        |
|               | gpt-3.5-turbo (discouraged!)                  |
| AWS Bedrock   | anthropic.claude-3-5-sonnet-20240620-v1:0     |
|               | meta.llama3-70b-instruct-v1:0                 |
|               | mistral.mixtral-8x7b-instruct-v0:1            |
