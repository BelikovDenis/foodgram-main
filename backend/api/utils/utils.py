def generate_text_content(data):
    """Генерирует текстовое содержимое для списка покупок."""
    lines = []
    for item in data:
        name = item['name']
        unit = item['unit']
        total = item['total']
        lines.append(f'{name} ({unit}) — {total}')
    return '\n'.join(lines)
