import json
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

def get_ban_list():
    words_dataset = None
    with open('src/app/services/banword_service/banwords.json', 'r') as f:
        words_dataset = json.loads(f.read())
        f.close()
    return words_dataset


CRITICAL_PERCENT = 80
words_dataset = get_ban_list()


def match_banword_percent(word: str):
    result = process.extractOne(word, get_ban_list(), scorer=fuzz.partial_ratio)
    return (result[1] > CRITICAL_PERCENT, result[1], result[0])

