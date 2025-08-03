import csv
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle


def generate_text_content(data):
    """Генерирует текстовое содержимое для списка покупок."""
    lines = []
    for item in data:
        name = item['name']
        unit = item['unit']
        total = item['total']
        lines.append(f'{name} ({unit}) — {total}')
    return '\n'.join(lines)


def generate_csv_content(data):
    """Генерирует CSV содержимое для списка покупок."""
    output = []
    writer = csv.writer(output)
    writer.writerow(['Ингредиент', 'Единица измерения', 'Количество'])
    for item in data:
        writer.writerow([item['name'], item['unit'], item['total']])
    return '\n'.join([','.join(map(str, row)) for row in output])


def generate_pdf(data):
    """Генерирует PDF документ со списком покупок."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title = Paragraph('Список покупок', title_style)
    elements.append(title)
    elements.append(Paragraph('<br/><br/>', styles['Normal']))

    if data:
        table_data = [['Ингредиент', 'Единица измерения', 'Количество']]
        for item in data:
            table_data.append([
                item['name'],
                item['unit'],
                str(item['total'])
            ])
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph(
            'Ваш список покупок пуст.',
            styles['Normal']
        ))

    doc.build(elements)
    buffer.seek(0)
    return buffer
