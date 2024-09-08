
import re
def slugify(title):
    symbol_mapping = (
        (' ', '-'),
        ('<', '-'),
        ('>', '-'),
        ('{', '-'),
        ('}', '-'),
        ('[', '-'),
        (']', '-'),
        ('`', '-'),
        ('"', '-'),
        ("'", '-'),
        ('#', '-'),
        ('.', '-'),
        (',', '-'),
        ('!', '-'),
        ('?', '-'),
        ("'", '-'),
        ('"', '-'),
        (';', '-'),
        ('/', '-'),
        ('|', '-'),
        (';', '-'),
        ('ə', 'e'),
        ('ı', 'i'),
        ('ö', 'o'),
        ('ğ', 'g'),
        ('ü', 'u'),
        ('ş', 's'),
        ('ç', 'c'),
    )
    
    title_url = title.strip().lower()

    for before, after in symbol_mapping:
        title_url = title_url.replace(before, after)

    valid_characters = re.compile(r'[^a-zA-Z0-9._-]')
    sanitized_name = valid_characters.sub('_', title_url)

    return sanitized_name

