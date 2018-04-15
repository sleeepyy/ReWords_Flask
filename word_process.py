import re
def process(path):
    pattern = re.compile(r'\s*/.+/\s*')
    with open(path, 'r', encoding='utf-8') as f:
        lines = [pattern.split(line.strip()) for line in filter(lambda x: x!='\n', f.readlines())]
        return lines

if __name__ == "__main__":
    print(process('CET4.words'))
