import os
import sys

# Add the current directory to sys.path so we can import the module if needed, 
# but it's easier to just parse the file or exec it.

try:
    with open('scripts/generate_quiz_sem4.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We can use ast to safely evaluate the SEM4 dictionary
    import ast
    
    # Find the start and end of the SEM4 dictionary definition
    # This is a bit fragile if the file changes format, but let's try
    start_marker = "SEM4 = {"
    end_marker = "}\n\ndef build_js_block"
    
    start_index = content.find(start_marker)
    end_index = content.find(end_marker) + 1
    
    if start_index != -1 and end_index != -1:
        dict_str = content[start_index + len("SEM4 = "):end_index]
        sem4_dict = ast.literal_eval(dict_str)
        
        for key, value in sem4_dict.items():
            print(f"{key}: {len(value)} questions")
            # Check for duplicate questions
            questions = [q['q'] for q in value]
            if len(questions) != len(set(questions)):
                print(f"  WARNING: {key} has duplicate questions!")
                from collections import Counter
                counts = Counter(questions)
                for q, count in counts.items():
                    if count > 1:
                        print(f"    Duplicate: {q}")
    else:
        print("Could not find SEM4 dictionary in file")

except Exception as e:
    print(f"Error: {e}")
