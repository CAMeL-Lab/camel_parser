

def get_lines_to_parse(lines, word_limit):
    
    sentence_limit = None
    for i, line in enumerate(lines):
        word_limit -= len(line.split())
        if word_limit < 0:
            sentence_limit = i
            break
    if not sentence_limit:
        sentence_limit = len(lines)
    return lines[:sentence_limit], lines[sentence_limit:]

def unparsed_lines_to_conll(lines):
    lines_to_print = []
    for line in lines:
        lines_to_print.extend((f"# text = {line}", f"# treeTokens = {line}"))
        words = line.split()
        lines_to_print.extend(
            f"{i + 1}\t{words[i]}\t_\t_\t_\t_\t0\t---\t_\t_"
            for i in range(len(words))
        )
    return lines_to_print
            

if __name__ == '__main__':
    lines = ['test line 1', 'test line 2', 'test line 3', 'test line 4']
    
    word_limit = 8
    
    lines_to_parse, lines_to_ignore = get_lines_to_parse(lines, word_limit)
    print(lines_to_parse)
    print()
    print(lines_to_ignore)
    # lines = ["لونغ بيتش (الولايات المتحدة) 15-7 (إف ب) - كل شيء تغير في حياة المتشرد ستيفن كنت عندما عثرت عليه شقيقته بعد عناء طويل لتبلغه بأنه ورث 300 ألف دولار وبأنه بات قادرا على وضع حد لعشرين سنة من حياة التشرد في شوارع مدينة لونغ بيتش في ولاية كاليفورنيا."]
    
    # to_print = unparsed_lines_to_conll(lines)
    import pdb; pdb.set_trace()