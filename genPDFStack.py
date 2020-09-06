import click
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm, inch
from reportlab.platypus import Image    


@click.option('-I', '--use-inch', 'unit', 
    flag_value=inch, 
    default=True, 
    help='Use inch for measurements (default)')

@click.option('-M', '--use-mm', 'unit', 
    flag_value=mm, 
    help='Use millimeters for measurements')

@click.option('-o','--output', 
    type=click.File('wb'), 
    default='./test/output.pdf', 
    help='Specify the output path and filename (default is current working directory)')

@click.option('-s', '--page-size', 
    type=click.Tuple([float, float]), 
    default=(8.5, 11), 
    metavar='<width> <height>', 
    help='Specify the size of the output file')


@click.argument('images', 
    nargs=-1, 
    type=click.File('rb'))

@click.argument('text', 
    nargs=1, 
    type=click.File('r'))


@click.command()

def main(output, unit, page_size, images):
    """This tool generates printable PDF documents from some input IMAGES and TEXT"""
    width, height = tuple(unit * el for el in page_size)
    img_border = 0.25 * inch
    pdf = canvas.Canvas(output, pagesize=(width, height))

    next_x = img_border
    next_y = height - 3.5*inch - img_border

    for img in images:
        if (next_x + 3.5*inch + img_border > width):
            next_x = img_border
            next_y = next_y - 2*img_border - 3.5*inch
            if (next_y < 0):
                pdf.showPage()
                next_x = img_border
                next_y = height - 3.5*inch - img_border
        pdf.drawImage(img.name, next_x , next_y , 3.5*inch, 3.5*inch)
        next_x = next_x + 3.5*inch + 2*img_border   

    pdf.showPage()
    pdf.save()
