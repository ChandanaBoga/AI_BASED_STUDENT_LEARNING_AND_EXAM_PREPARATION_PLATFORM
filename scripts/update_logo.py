import os
import re

DIR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

# re.DOTALL ensures \s* matches newlines (multi-line HTML elements)
OLD_PATTERN = re.compile(
    r'<div class="size-10 bg-primary rounded-xl flex items-center justify-center '
    r'text-white shadow-lg shadow-primary/20">\s*'
    r'<span class="material-symbols-outlined text-[^"]+">waves</span>\s*'
    r'</div>',
    re.DOTALL
)

NEW_REPLACEMENT = (
    '<div class="size-10 rounded-xl overflow-hidden shadow-lg shadow-primary/20 '
    'bg-white border border-blue-100 dark:border-blue-900/30 '
    'flex items-center justify-center p-0.5">\n'
    '    <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSnVWZJEPadz-8y7DDfGxA_egH65p_m1p0ulQ&s" '
    'alt="Logo" class="w-full h-full object-contain rounded-lg">\n'
    '</div>'
)


def update_logos_in_directory(dir_path: str) -> int:
    """
    Walk all HTML files in `dir_path`, replacing old wave-logo divs
    with the new logo img. Returns total number of files updated.
    """
    count = 0
    for root, _, files in os.walk(dir_path):
        for filename in files:
            if not filename.endswith('.html'):
                continue

            filepath = os.path.join(root, filename)

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                if OLD_PATTERN.search(content):
                    new_content = OLD_PATTERN.sub(NEW_REPLACEMENT, content)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"[UPDATED] {filename}")
                    count += 1

            except (OSError, UnicodeDecodeError) as e:
                print(f"[SKIPPED] {filename} — {e}")

    return count


if __name__ == "__main__":
    total = update_logos_in_directory(DIR_PATH)
    print(f"\nDone. Total files updated: {total}")
