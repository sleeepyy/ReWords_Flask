import re

def process_words(path):
    pattern = re.compile(r'\s*/.+/\s*')
    words = dict()
    with open(path, 'r', encoding='utf-8') as f:
        for line in filter(lambda x: x!='\n', f.readlines()):
            # print(line)
            word = pattern.split(line.strip())
            if len(word) == 2:
                words[word[0]] = word[1]
            else:
                assert len(word) == 1
                splited = word[0].split()
                words[splited[0]] = ''.join(splited[1:])
        return words

if __name__ == "__main__":
    print(process_words('CET4.words'))
