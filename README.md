# EHRmonize

Welcome to `EHRmonize`, a Python package to abstract medical concepts using large language models.

[![arXiv](https://img.shields.io/badge/arXiv-2407.00242-b31b1b.svg)](https://arxiv.org/abs/2407.00242)
[![Python 3.9](https://img.shields.io/badge/python-3.9-red.svg)](https://www.python.org/downloads/release/python-390/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![stability-beta](https://img.shields.io/badge/stability-beta-33bbff.svg)](https://github.com/mkenney/software-guides/blob/master/STABILITY-BADGES.md#beta)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-EHRmonize-blue)](https://huggingface.co/datasets/AIWongLab/ehrmonize)
[![PyPI version](https://badge.fury.io/py/ehrmonize.svg)](https://badge.fury.io/py/ehrmonize)
[![Documentation Status](https://readthedocs.org/projects/ehrmonize/badge/?version=latest)](https://ehrmonize.readthedocs.io/en/latest/?badge=latest)
[![PR Welcome Badge](https://badgen.net/https/pr-welcome-badge.vercel.app/api/badge/aiwonglab/ehrmonize)](https://github.com/aiwonglab/ehrmonize/issues?q=archived:false+is:issue+is:open+sort:updated-desc+label%3A%22help%20wanted%22%2C%22good%20first%20issue%22)


## Suggested Citation

> Matos, J., Gallifant, J., Pei, J., & Wong, A. I. (2024). EHRmonize: A framework for medical concept abstraction from electronic health records using large language models. arXiv. https://arxiv.org/abs/2407.00242

```
@article{
    matos2024ehrmonize,
      title={EHRmonize: A Framework for Medical Concept Abstraction from Electronic Health Records using Large Language Models}, 
      author={João Matos and Jack Gallifant and Jian Pei and A. Ian Wong},
      year={2024},
      eprint={2407.00242},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2407.00242}, 
}
```

## Documentation 

For documentation, please see: https://ehrmonize.readthedocs.io/. We are currently working on a demo that will soon be available on Google Colaboratory.

## Motivation
Processing and harmonizing the vast amounts of data captured in complex electronic health records (EHR) is a challenging and costly task that requires clinical expertise. Large language models (LLMs) have shown promise in various healthcare-related tasks. We herein introduce `EHRmonize`, a framework designed to abstract EHR medical concepts using LLMs.

## Rationale
`EHRmonize` is designed with two main components: a corpus generation and an LLM inference pipeline. The **first step** entails querying the EHR databases to extract and the text/concepts across various data domains that need categorization. The **second step** employs LLM few-shot prompting across different tasks. The objective is to leverage the vast medical text exposure of LLMs to convert raw input medication data into useful, predefined classes.

## Dataset 
Our curated and labeled dataset is accessible on
[HuggingFace](https://huggingface.co/datasets/AIWongLab/ehrmonize).

## Current supported tasks

| Type          | Task                          |
|---------------|-------------------------------|
| Free-text     | [*task_generic_drug* ](https://ehrmonize.readthedocs.io/en/latest/autoapi/ehrmonize/ehrmonize/index.html#ehrmonize.ehrmonize.EHRmonize.task_generic_route)           |
|               | [task_generic_route](https://ehrmonize.readthedocs.io/en/latest/autoapi/ehrmonize/ehrmonize/index.html#ehrmonize.ehrmonize.EHRmonize.task_generic_drug)          |
| Multiclass    | [task_multiclass_drug](https://ehrmonize.readthedocs.io/en/latest/autoapi/ehrmonize/ehrmonize/index.html#ehrmonize.ehrmonize.EHRmonize.task_multiclass_drug)              |
| Binary        | [task_binary_drug](https://ehrmonize.readthedocs.io/en/latest/autoapi/ehrmonize/ehrmonize/index.html#ehrmonize.ehrmonize.EHRmonize.task_binary_drug) |
| Custom        | [task_custom](https://ehrmonize.readthedocs.io/en/latest/autoapi/ehrmonize/ehrmonize/index.html#ehrmonize.ehrmonize.EHRmonize.task_custom)                      |


## Current supported models / engines / APIs

| API           | model_id                                      |
|---------------|-----------------------------------------------|
| [OpenAI](https://platform.openai.com/docs/api-reference/chat/create)        | gpt-4                                         |
|               | gpt-4o                                        |
|               | gpt-3.5-turbo (discouraged!)                  |
| [AWS Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html)   | anthropic.claude-3-5-sonnet-20240620-v1:0     |
|               | meta.llama3-70b-instruct-v1:0                 |
|               | mistral.mixtral-8x7b-instruct-v0:1            |
