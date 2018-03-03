from dotenv import load_dotenv
import os
from os.path import join,dirname


dotenv_path=join(dirname(__file__),'.env')
load_dotenv(dotenv_path)

API_TOKEN=os.environ.get("API_TOKEN")

DEFAULT_REPLY="ちょっと何言ってるかよくわかんないです"

PLUGINS=['plugins']
