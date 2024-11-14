# IMPORT RELEVANT MODULES
from pathlib import Path
from camel_tools.utils.charmap import CharMapper
from pandas import read_csv
from src.classes import TextParams
from src.initialize_disambiguator.disambiguator_interface import get_disambiguator
from src.data_preparation import get_tagset, parse_text
from src.utils.model_downloader import get_model_name
from src.conll_output import save_to_file, text_tuples_to_string


if __name__ == '__main__':

    ### SETTING UP REQUIRED ITEMS FOR THE DISAMBIGUATOR AND PARSER
    ### You could leave all this unchanged and go down to the sentences section.
    # Set up parser model
    root_dir = Path(__file__).parent
    model_path = root_dir/"models"
    parse_model = "catib"


    # camel_tools import used to clean text
    arclean = CharMapper.builtin_mapper("arclean")

    #
    ### Clitic features used with disambiguator
    #
    clitic_feats_df = read_csv(root_dir / 'data/clitic_feats.csv')
    clitic_feats_df = clitic_feats_df.astype(str).astype(object) # so ints read are treated as string objects

    ### Set up parsing model 
    # (download defaults models, and get correct model name from the models directory)
    model_name = get_model_name(parse_model, model_path=model_path)
    
    # 
    ### NO NEED TO CHANGE
    ### get tagset (depends on model)
    #
    tagset = get_tagset(parse_model)
    
    #
    ### Initialize disambiguator. To use s31, replace r13 with calima-msa-s31 (see 'Using another morphology database' in the README).
    disambiguator = get_disambiguator("bert", "r13")

    ### SENTENCES SECTION
    ### YOUR SENTENCE CODE HERE. You can also create a for loop and read multiple files, running the remaining code below for each file).
    sentences = [
        "فاتصل علي أحد أصدقائي وقال لي: إني متواجد أمام بيتك،",
        "فنزلت وسلمت عليه قبل أن أسافر،",
        "وبعدها جاء أصدقائي وذهبت معهم،",
        "كان في طريقي إلى المطار حادث وخشيت أن تفوتني الرحلة،",
        "وهل سيشرحونها؟"
    ]


    # pass your sentences and other variables to TextParams (the last variable, morphology_db_type, can be left empty).
    file_type_params = TextParams(sentences, model_path/model_name, arclean, disambiguator, clitic_feats_df, tagset, "")
    parsed_text_tuples = parse_text("text", file_type_params)
    
    trees_string = text_tuples_to_string(parsed_text_tuples, sentences=sentences) # NOTE: we use the original sentences in the final conll file.
    
    # optional: save your conll file by passing the trees_string and output path + new name of file
    # The new file would be of the type .conllx
    # save_to_file(
    #     trees_string,
    #     Path(output_path) / new_name
    # )