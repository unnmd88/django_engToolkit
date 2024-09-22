import toolkit.sdp_lib as sdp_lib
import os

from dotenv import load_dotenv

load_dotenv()

DEBUG = True if os.getenv('DEBUG') in ('1', 'True') else False

print(DEBUG)




