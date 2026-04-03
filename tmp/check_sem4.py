import ast, sys

try:
    content = open('scripts/generate_quiz_sem4.py', encoding='utf-8').read()
    compile(content, 'generate_quiz_sem4.py', 'exec')
    print("Syntax OK")
except SyntaxError as e:
    print(f"SyntaxError at line {e.lineno}: {e.msg}")
    print(f"Text: {e.text}")
