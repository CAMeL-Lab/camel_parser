# -*- coding: utf-8 -*-

import datetime
import os
import random
from src.initialize_disambiguator.disambiguator_interface import get_disambiguator
from src.parse_limit import get_lines_to_parse, unparsed_lines_to_conll
from src.conll_output import text_tuples_to_string
from src.data_preparation import get_file_type_params, parse_text
from flask import request, Flask
from pandas import read_csv
from camel_tools.utils.charmap import CharMapper


from flask_cors import CORS
import sys

sys.path.insert(0, "camel_parser/src")

from dotenv import load_dotenv

load_dotenv(".env")


project_dir = os.path.expanduser(".")
# for local dev
# project_dir = os.path.expanduser('.')

# camel_tools import used to clean text
arclean = CharMapper.builtin_mapper("arclean")

#
### Get clitic features
#
clitic_feats_df = read_csv(f"{project_dir}/data/clitic_feats.csv")
# so ints read are treated as string objects
clitic_feats_df = clitic_feats_df.astype(str).astype(object)


# disambiguator = get_disambiguator("bert", "calima-msa-s31")

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = f"{os.path.expanduser(project_dir)}/client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
# os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
API_SERVICE_NAME = "drive"
API_VERSION = "v3"

PARSE_WORD_LIMIT = 100

app = Flask(__name__)
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See https://flask.palletsprojects.com/quickstart/#sessions.
app.secret_key = os.getenv("FLASK_SECRET")

# app.config['CORS_HEADERS'] = 'Content-Type'

# cors = CORS(app, resources={r"/test": {"origins": 'https://voluble-fudge-4fc88e.netlify.app/'}})
cors = CORS(app, supports_credentials=True)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/parse_data", methods=["POST"])
def parse_data():
    all_lines = request.get_json()["sentences"]
    parser_type = request.get_json()["parserType"]
    file_type = "text"

    if parser_type == "ar_catib":
        parser_model_name = "CAMeLBERT-CATiB-biaffine.model"
        tagset = "catib6"
    elif parser_type == "ar_ud":
        parser_model_name = "CAMeLBERT-UD-biaffine.model"
        tagset = "ud"
    else:
        # just in case user messes with html
        return

    disambiguator = get_disambiguator("mle", "calima-msa-s31")

    # will parse lines for a total of 100 words
    lines, lines_to_ignore = get_lines_to_parse(all_lines, PARSE_WORD_LIMIT)

    file_type_params = get_file_type_params(
        lines,
        file_type,
        "",
        f"{project_dir}/models/{parser_model_name}",
        arclean,
        disambiguator,
        clitic_feats_df,
        tagset,
        "calima-msa-s31",
    )
    parsed_text_tuples = parse_text(file_type, file_type_params)

    string_lines = text_tuples_to_string(parsed_text_tuples, 'text', sentences=lines)

    # add parsed lines to unparsed lines
    if lines_to_ignore:
        lines_to_ignore = unparsed_lines_to_conll(lines_to_ignore)
        string_lines = string_lines + lines_to_ignore

    parsed_data = "\n".join(string_lines)

    new_id = datetime.datetime.now().strftime("%s") + str(int(random.random() * 100000))

    with open(f"{project_dir}/data/temp_parsed/{new_id}", "w") as f:
        f.write(parsed_data)

    return new_id


@app.route("/get_parsed_data", methods=["GET"])
def get_parsed_data():
    data_id = request.args.get("data_id")
    conll_file_path = f"{project_dir}/data/temp_parsed/{data_id}"

    data = []
    with open(conll_file_path, "r") as f:
        data = f.readlines()
    os.remove(conll_file_path)

    return "".join(data)


@app.route("/get_gapi_credentials", methods=["GET"])
def get_gapi_credentials():
    return {
        "apiKey": os.getenv("GCP_API_KEY"),
        "clientId": os.getenv("GCP_CLIENT_ID"),
        "discovertDocs": [os.getenv("GCP_DISCOVERY_DOC")],
    }


@app.route("/get_gis_credentials", methods=["GET"])
def get_gis_credentials():
    return {"client_id": os.getenv("GCP_CLIENT_ID"), "scope": SCOPES}


if __name__ == "__main__":
    project_dir = os.path.expanduser(".")
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    # os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Specify a hostname and port that are set as a valid redirect URI
    # for your API project in the Google API Console.
    # app.run('localhost', 8080, debug=True)
