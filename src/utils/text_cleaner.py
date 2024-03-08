from camel_tools.tokenizers.word import simple_word_tokenize
from camel_tools.utils.dediac import dediac_ar
from camel_tools.utils.normalize import normalize_unicode
from camel_tools.utils.charmap import CharMapper

def clean_line(line, arclean):
    return simple_word_tokenize(arclean(dediac_ar(normalize_unicode(line.strip()))))

def split_lines_words(lines):
    return [line.strip().split() for line in lines]

def clean_mad(lines):
    new_lines = []
    for line in lines:
        new_line = []
        for word in line:
            # replacing underscore with mad character
            if word == 'ـ':
                new_line.append('_')
            else:
                new_line.append(word)
        new_lines.append(new_line)
    return new_lines

def clean_lines(lines, arclean):
    return [clean_line(line, arclean) for line in lines]

if __name__ == '__main__':
    lines = []
    with open('data/sample_text.txt', 'r') as f:
        lines = f.readlines()
    
    arclean = CharMapper.builtin_mapper("arclean")
    new_lines = clean_lines(lines, arclean)
