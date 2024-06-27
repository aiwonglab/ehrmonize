Usage
=====

.. _installation:

Installation
------------

To use EHRmonize, first install it using pip:

.. code-block:: console

   $ pip install ehrmonize

Using EHRmonize
---------------

To harmonize EHR data and retrieve generic drug names, you can use the ``EHRmonize`` class and its methods.
Below is an example of how to set up and use EHRmonize:

.. code-block:: python


   from ehrmonize import EHRmonize
   import pandas as pd
   data = pd.read_csv("hf://datasets/AIWongLab/ehrmonize/ehrmonize.csv")
      
   shots = [
        "An input drugname 'vancocin' would be classified as 'vancomycin'.",
   ]

   ehrm = EHRmonize(
      model_id='gpt-4o',
      temperature=0.1,
      max_tokens=64,
      openai_api_key=userdata.get('OPENAI_API_KEY'), # defined via secrets
      )  

    ehrm.config_prompting(
      n_shots=1,
    )

    ehrm.set_task(
      task='task_generic_route',
      possible_shots=shots,
    )

   data['predicted_generic'] = ehrm.predict(
      input=data['drug'],
      progress_bar=True
   )

   # display the original drug name, labeled generic name, and predicted generic name
   display(data[['drug', 'generic_name', 'predicted_generic']])
