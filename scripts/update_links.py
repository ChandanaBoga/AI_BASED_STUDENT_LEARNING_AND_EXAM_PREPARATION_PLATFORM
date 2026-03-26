import os
import re

dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

old_syl_pattern = r'https://drive\.google\.com/drive/folders/1t2UfM4gsgDVyaxUx1jfItRaBvMdGNnGg'
new_syl = r'https://drive.google.com/drive/folders/1t2UfM4gsgDVyaxUx1jfItRaBvMdGNnGg?usp=drive_link'

old_qa_pattern = r'https://drive\.google\.com/drive/(u/1/)?folders/1UkabLav3bgRFAMtd2M1KX9NHDyZRvFab'
new_qa = r'https://drive.google.com/drive/folders/1UkabLav3bgRFAMtd2M1KX9NHDyZRvFab?usp=drive_link'

count = 0
for root, _, files in os.walk(dir_path):
    for f in files:
        if f.endswith('.html'):
            filepath = os.path.join(root, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            new_content = re.sub(old_syl_pattern, new_syl, content)
            new_content = re.sub(old_qa_pattern, new_qa, new_content)
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print(f'Updated {f}')
                count += 1

print(f'Total files updated: {count}')
