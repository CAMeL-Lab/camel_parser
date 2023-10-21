CamelParser
=============

.. image:: https://img.shields.io/pypi/l/camel-tools.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT License

Introduction
------------

CamelParser is an open-source Python-based Arabic dependency parser targeting two popular Arabic dependency formalisms, 
the Columbia Arabic Treebank (CATiB), and Universal Dependencies (UD).

The CamelParser pipeline handles the processing of raw text and roduces tokenization, part-of-speech and rich morphological features.
For disambiguation, users can choose between the BERT unfactored disambiguator, or a lighter Maximum Likelihood Estimation (MLE) disambiguator, both of which are included in CAMeL Tools. For depednecy parsing, we use the SuPar Biaffine Dependency Parser.


Installation
------------

To install the required packages, run

.. code-block:: bash

    pip install -r requirements.txt

Setting up the morphology db
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You must install the morphology db for CamelParser to work.

1. Install camel_tools v1.5.2 or later (you can check this using camel_data -v)

2. Download the camel data for the BERT unfactored (MSA) model, as well as the morphology database:

.. code-block:: bash

    camel_data -i morphology-db-msa-s31 
    camel_data -i disambig-bert-unfactored-msa
    
3. Download the LDC2010L01 from the ldc downloads:
    - go to https://catalog.ldc.upenn.edu/organization/downloads
    - search for LDC2010L01.tgz and download it

4. DO NOT EXTRACT LDC2010L01.tgz! We'll use the following command from camel tools to install the db:

.. code-block:: bash

    camel_data -p morphology-db-msa-s31 /path/to/LDC2010L01.tgz

Citation
--------

If you use CamelParser in your research, please cite

.. code-block:: bibtex

    @inproceedings{Elshabrawy:2023:camelparser,
        title = "{CamelParser2.0: A State-of-the-Art Dependency Parser for Arabic}",
        author = {Ahmed Elshabrawy and 
    Muhammed AbuOdeh and
    Go Inoue and
    Nizar Habash} ,
        booktitle = {Proceedings of The First Arabic Natural Language Processing Conference (ArabicNLP 2023)},
        year = "2023"
    }

and

.. code-block:: bibtex

   @inproceedings{obeid-etal-2020-camel,
      title = "{CAM}e{L} Tools: An Open Source Python Toolkit for {A}rabic Natural Language Processing",
      author = "Obeid, Ossama  and
         Zalmout, Nasser  and
         Khalifa, Salam  and
         Taji, Dima  and
         Oudah, Mai  and
         Alhafni, Bashar  and
         Inoue, Go  and
         Eryani, Fadhl  and
         Erdmann, Alexander  and
         Habash, Nizar",
      booktitle = "Proceedings of the 12th Language Resources and Evaluation Conference",
      month = may,
      year = "2020",
      address = "Marseille, France",
      publisher = "European Language Resources Association",
      url = "https://www.aclweb.org/anthology/2020.lrec-1.868",
      pages = "7022--7032",
      abstract = "We present CAMeL Tools, a collection of open-source tools for Arabic natural language processing in Python. CAMeL Tools currently provides utilities for pre-processing, morphological modeling, Dialect Identification, Named Entity Recognition and Sentiment Analysis. In this paper, we describe the design of CAMeL Tools and the functionalities it provides.",
      language = "English",
      ISBN = "979-10-95546-34-4",
   }

and if you use the BERT unfactored disambiguator, please also cite

.. code-block:: bibtex

    @inproceedings{Inoue:2022:Morphosyntactic,
        title = "Morphosyntactic Tagging with Pre-trained Language Models for {A}rabic and its Dialects",
        author = "Inoue, Go  and
        Khalifa, Salam  and
        Habash, Nizar",
        booktitle = "Findings of the Association for Computational Linguistics: ACL 2022",
        month = may,
        year = "2022",
        address = "Dublin, Ireland",
        publisher = "Association for Computational Linguistics",
        url = "https://aclanthology.org/2022.findings-acl.135",
        doi = "10.18653/v1/2022.findings-acl.135",
        pages = "1708--1719",
        abstract = "We present state-of-the-art results on morphosyntactic tagging across different varieties of Arabic using fine-tuned pre-trained transformer language models. Our models consistently outperform existing systems in Modern Standard Arabic and all the Arabic dialects we study, achieving 2.6{\%} absolute improvement over the previous state-of-the-art in Modern Standard Arabic, 2.8{\%} in Gulf, 1.6{\%} in Egyptian, and 8.3{\%} in Levantine. We explore different training setups for fine-tuning pre-trained transformer language models, including training data size, the use of external linguistic resources, and the use of annotated data from other dialects in a low-resource scenario. Our results show that strategic fine-tuning using datasets from other high-resource dialects is beneficial for a low-resource dialect. Additionally, we show that high-quality morphological analyzers as external linguistic resources are beneficial especially in low-resource settings.",
    }