from hitchrun import cwd

def cat(filename):
    print(cwd.joinpath(filename).bytes().decode('utf8'))
