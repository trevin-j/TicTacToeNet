'''
This module is for retrieving input from user.
This comes in handy because it makes it super easy to retrieve input from a file for testing as if a user entered it.
'''

TEST_MODE = 0
RELEASE_MODE = 1

mode = RELEASE_MODE
test_file = None
file_line = 0

def set_test_file(file_name: str) -> None:
    global test_file
    test_file = file_name

def set_mode(new_mode: int) -> None:
    global mode
    mode = new_mode

def get_input(prompt: str) -> str:
    if mode == TEST_MODE:
        return test_input(prompt)
    else:
        return input(prompt)

def test_input(prompt: str) -> str:
    global test_file
    global file_line
    if test_file is None:
        raise Exception('Test file not set')
    with open(test_file, 'r') as f:
        for i in range(file_line):
            f.readline()
        file_line += 1
        inp = f.readline().strip()
        print(f'{prompt}{inp}')
        return inp