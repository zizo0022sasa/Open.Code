import sys
sys.path.insert(0, r"D:\SMS\.hRhR_gateway-service\_antigravity_workspace")
from file_editor_agent import match_and_replace_block, validate_python_syntax

# 1. Test CRLF vs LF
orig = "def foo():\r\n    print('hello')\r\n"
search = "    print('hello')\n"
rep = "    print('world')\n"
res, mtype = match_and_replace_block(orig, search, rep)
print("1. CRLF/EOL Test:", mtype, "--> Success:", "world" in res)

# 2. Test whitespace collapse
orig2 = "x = 10\n    y   =   20\n"
search2 = "y = 20"
rep2 = "y = 99"
res2, mtype2 = match_and_replace_block(orig2, search2, rep2)
print("2. Whitespace Collapse Test:", mtype2, "--> Success:", "99" in res2)

# 3. Test AST validation
valid_py = "def test():\n    return 42\n"
invalid_py = "def test():\n    return 42 broken syntax ++--\n"
print("3. AST Valid Test:", validate_python_syntax(valid_py))
print("4. AST Invalid Test:", validate_python_syntax(invalid_py))

