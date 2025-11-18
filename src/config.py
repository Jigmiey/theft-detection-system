from dotenv import load_dotenv
import os

load_dotenv()

def get_setting(key:str,default:str|None=None) -> str|None:
    return os.getenv(key,default)

if __name__=="__main__":
    print("OPENAI api key present?",bool(get_setting("OPEN_API_KEY")))


