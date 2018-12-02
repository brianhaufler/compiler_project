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


Semantic Actions 3 Update:
----------------------------
Default test file is "phase3-1.txt". Will run if command is "python3 compiler.py" with no listed test file.

Moved the Semantic Actions into their own file semantic_actions.py. Also created quadruple.py for the
quadruples and the quadruple class

Initialized the local table and the global table within the semantic actions class
Also created a boolean value "print_parse_trace" in the ParseData class. This is initialized to True,
but can be changed to False if we do not want to see the parseData

There was an error in semantic actions 2 that I wasn't able to fix yet. When an array statement is used
(ex: x[b] := c), the type of b is compared to c when it should be the type of x compared to c. I will try to fix
this before the next phase

Semantic Actions 3 Update (Part 2):
------------------------------------
The initial Semantic Actions 3 was a bit sloppy, so I decided to submit this as well. I don't
expect this to be graded (instead of the previous submission), but I wanted you to know that
I've corrected most of those errors.

Changes:
- Get_opcode can now take in RELOPs and "AND" and "OR"
- Fixed multiple "Etype" instead of "EType errors"
- Fixed multiple ".getNextQuad" instead of ".getNextQuad()" errors
- Put several "self.semantic_stack.append(EType.ARITHMETIC)"s in the right place
    (before some were in else statements when they shouldn't have been or vice versa)
- Fixed the merge function (Append doesn't work on two lists).
- The previously noted error in semantic actions 2 (regarding array statements) is now fixed.
    I'm not sure if that's due to the newly implemented actions in part 3.
- Added self.actions_tested = [] in Semantic Actions class for debugging purposes

For the test file "phase3-8.txt", it breaks because there is an extra "}" at the
end of the file when there shouldn't be. The program can technically still run
even if that } remains there, so I'm still deciding whether I want to allow the
file to work.






