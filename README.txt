README for lexical_analyser.py

Running the file:
    First ensure that you have Python3 installed
    Then add the test files into the directory containing lexical_analyser.py
    Then, from the same directory, run the following command from the terminal:
        "python3 lexical_analyser.py [test_file]"
    For example:
        "python3 lexical_analyser.py lextest_4.txt"

    The output will be the list of tokens, each separated by a newline
    If the program failed, there will also be an error message

Additional Notes:
    1) For my compiler design, I decided that a string such as "12.34e-SURPRISE" is
    an ill-formed constant even though "SURPRISE" could be an integer constant.
    Likewise "5.3ea" is ill-formed even though "a" could also be an int constant.
    This could have been determined at syntax analysis, but I decided that my lexer
    should handle the duty

    2) The maximum token length allowed is 30

    3) The names of my test files are aligned with the lexer specification
    token list, rather than the names listed in the solution files


Parser Update:
--------------------
Since the last update, I have created a master "compiler.py" file that runs the entire program and have split up the components into "lexer.py" and "parser.py".
Running the program remains the same, except you should call "python3 compiler.py [test_file]"
These test_files must be actual programs, not just tokens. The output for this program will simply be "Accept" or an
Error message, depending on whether the parser accepts the output or not. Additionally, the program could fail in the lexer phase.
The included test_file is "ult-corrected.txt"


dump_stack(parse_data) can be used to print the current contents of the stack. Provided, of course, that
you give the function the instance of the ParseData data class that contains the stack. Additionally I
left several print statements in the parser code. If uncommented, these will print out the steps of the parse.
This will look very similar to the "Completed parse" example that we were given.


Semantic Actions 1 Update:
-------------------------------
Running the program is the same as before.

Changes
- I've added the SemanticAction class to the compiler.py file. This class may move in future updates.
- In parser.py, I initialized parser_local_table on line 9. Additionally I added the semantic actions to the grammar
    and added an option for that to be the next token that is popped "elif (isinstance(symbol, int)):" on line 30.
    There's also a peek_prev_token method in the ParserData class
