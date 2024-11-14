CamelParser
=============

.. image:: https://img.shields.io/pypi/l/camel-tools.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT License

Introduction
------------

CamelParser is an open-source Python-based Arabic dependency parser targeting two popular 
Arabic dependency formalisms, the Columbia Arabic Treebank (CATiB), and Universal Dependencies (UD).

The CamelParser pipeline handles the processing of raw text and produces tokenization, 
part-of-speech and rich morphological features. For disambiguation, users can choose between 
the BERT unfactored disambiguator, or a lighter Maximum Likelihood Estimation (MLE) disambiguator, 
both of which are included in CAMeL Tools. For dependency parsing, we use the SuPar Biaffine Dependency Parser.


Installation
------------
1. Clone this repo

2. Set up a virtual environment using Python 3.9.16 (you can follow the tutorial `here <https://www.youtube.com/watch?si=g2zx-D0zdkL50knb&v=31WU0Dhw4sk&feature=youtu.be>`_).

Currently, CamelParser does not work with later versions of python due to issues with some dependencies.

3. Install the required packages:

.. code-block:: bash

    pip install -r requirements.txt

4. Download dependency parsing models:

.. code-block:: bash

    python download_models.py

Currently, two Arabic script models, CATiB and UD, will be downloaded from the CAMeL Lab's 
`parser models collection <https://huggingface.co/collections/CAMeL-Lab/camelparser-654a3df21f70b3b5e72f95d9>`_ 
on Hugging Face. More models will be added soon!

Examples
--------
The CamelParser allows users to pass either a string or a file containing **one or more** sentences.
Below are examples using the different *string* inputs that CamelParser accepts. 
We pass each example as a string using -s. 
However, we do recommend using the file method (-i) along with the path to the file
when passing multiple sentences.
You can also refer to the `sample_starting_point.py` to use the parser in your code, or for more advanced usage:

.. code-block:: bash

text_to_conll_cli.py

handle_multiple_texts.py

handle_multiple_conll_files.py

Passing text

.. code-block:: bash
    
    python text_to_conll_cli.py -f text -s "جامعة نيويورك أبو ظبي تنشر أول أطلس لكوكب المريخ باللغة العربية."

The verbose version of the above example (default values are shown)

.. code-block:: bash

    python text_to_conll_cli.py -f text -b r13 -d bert -m catib -s "جامعة نيويورك أبو ظبي تنشر أول أطلس لكوكب المريخ باللغة العربية."

Passing preprocessed text (cleaned and whitespace tokenized)

.. code-block:: bash
    
    python text_to_conll_cli.py -f preprocessed_text -s "جامعة نيويورك أبو ظبي تنشر أول أطلس لكوكب المريخ باللغة العربية ."

*Note that the difference between the -f text and preprocessed_text parser input settings is*
*that for text we use different utilities from CAMeL Tools to* 
`normalize unicode <https://camel-tools.readthedocs.io/en/latest/api/utils/normalize.html?highlight=normalize_unicode#camel_tools.utils.normalize.normalize_unicode>`_, 
`dediactritize <https://camel-tools.readthedocs.io/en/latest/api/utils/dediac.html?highlight=dediac_ar>`_, 
*clean the text using* 
`arclean <https://camel-tools.readthedocs.io/en/latest/api/utils/charmap.html?highlight=arclean#utility>`_, 
*and perform* 
`whitespace tokenization <https://camel-tools.readthedocs.io/en/latest/api/tokenizers/word.html?highlight=simple_word_tokenize#camel_tools.tokenizers.word.simple_word_tokenize>`_.

tokenized is used when 1) the text has already been tokenized, and 2) only dependency relations are needed; 
the POS tags and features will not be generated.

.. code-block:: bash
    
    python text_to_conll_cli.py -f tokenized -s "جامعة نيويورك أبو ظبي تنشر أول أطلس ل+ كوكب المريخ ب+ اللغة العربية ."

tokenized_tagged is used when the user has the tokens and POS tags. They should be passed as tuples.

.. code-block:: bash
    
    python text_to_conll_cli.py -f tokenized_tagged -s "(جامعة, NOM) (نيويورك, PROP) (أبو, PROP) (ظبي, PROP) (تنشر, VRB) (أول, NOM) (أطلس, NOM) (ل+, PRT) (كوكب, NOM) (المريخ, PROP) (ب+, PRT) (اللغة, NOM) (العربية, NOM) (., PNX)"


Using a custom model
------------------
You can use your own dependency parser models by

1. placing the model in the models directory (this directory is created when you run download_models.py, but you can create it yourself)

2. place your model in the models directory

3. when running one of the scripts, add -m [model_name]. Just type the model name WITHOUT the path.

Extending the code
------------------

You can also use different parts of the code to create your own pipeline. 
The handle_multiple_texts.py is an example of that. It can be used to parse a directory of text files, 
saving the resulting CoNLL-X files to a given output directory.

Using another morphology database
---------------------------------

Curently, the CamelParser uses CAMeLTools' default morphology database, the morphology-db-msa-r13.

For our paper, we used the calima-msa-s31 database. To use this database, 
follow these steps (note that you need an account with the LDC):


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

5. When running the main script, use -b and pass calima-msa-s31.

Citation
--------

If you find the CamelParser useful in your research, please cite

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