"""The parsing code requires that conll files have two newlines at the end. 
The functions below ensure that this is the case before parsing"""

def read_n_to_last_line(filename, n = 1):
    """Returns the nth before last line of a file (n=1 gives last line)
    
    from https://stackoverflow.com/questions/46258499/how-to-read-the-last-line-of-a-file-in-python"""
    num_newlines = 0
    with open(filename, 'rb') as f:
        try:
            for i in range(1, n+1):
                f.seek(-i, 2)    
                    # while num_newlines < n:
                    #     f.seek(-2, os.SEEK_CUR)
                    #     if f.read(1) == b'\n':
                    #         num_newlines += 1
        except OSError:
            f.seek(0)
        last_line = f.readline().decode()
    return last_line

def add_newlines(file_path, second_last_line, last_line):
    with open(file_path, 'a') as f:
        if second_last_line != '\n':
            f.write('\n')
        if last_line != '\n':
            f.write('\n')

def adjust_eof_newlines(file_path):
    second_last_line = read_n_to_last_line(file_path, 2)
    last_line = read_n_to_last_line(file_path, 1)
    if not (second_last_line == last_line == '\n'):
        add_newlines(file_path, second_last_line, last_line)