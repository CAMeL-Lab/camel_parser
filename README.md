# camel_parser

## Setting up the morphology db

1. Install camel_tools v1.5.2 or later (you can check this using camel_data -v)

2. Download the camel data for the BERT unfactored (MSA) model, as well as the morphology database:
    commands:

        camel_data -i morphology-db-msa-s31 
        camel_data -i disambig-bert-unfactored-msa

3. Download the LDC2010L01 from the ldc downloads:
    - go to https://catalog.ldc.upenn.edu/organization/downloads
    - search for LDC2010L01.tgz and download it

4. DO NOT EXTRACT LDC2010L01.tgz! We'll use the following command from camel tools to install the db:

        camel_data -p morphology-db-msa-s31 /path/to/LDC2010L01.tgz
