import json

from src.app.services.banword_service.to_generate_data import symbols, row_words


def generate_variations(word: str):
    translit_word = ''
    word = word.lower()
    for i in range(len(word)):
        ch = word[i]
        if len(symbols[ch]) < 2:
            translit_word += symbols[ch][0]
        else:
            result = []
            for tch in symbols[ch]:
                for variant in generate_variations(word[i + 1::]):
                    result.append(translit_word+tch+variant)
            return result
    return [translit_word]


def row_words_to_dataset(words: list):
    res_words = []
    for bword in words:
        for tword in generate_variations(bword):
            res_words.append(tword)
    with open('src/app/services/banword_service/banwords.json', 'w') as f:
        f.write(json.dumps(res_words, ensure_ascii=False))
        f.close()


def generate():
    row_words_to_dataset(row_words)
