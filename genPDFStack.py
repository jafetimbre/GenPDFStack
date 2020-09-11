import click
import math
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm, inch
from reportlab.platypus import Image, Frame, Paragraph, SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

@click.group()

def main():
    pass

@click.option('-I', '--use-inch', 'unit', 
    flag_value=inch, 
    default=True, 
    help='Use inches for measurement (default)')

@click.option('-M', '--use-mm', 'unit', 
    flag_value=mm, 
    help='Use millimeters for measurement')

@click.option('-o','--output', 
    type=click.File('wb'), 
    default='./output.pdf', 
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


@main.command(name='with')

def simple(output, unit, page_size, images, text):
    """
    Generates the pdfstack from some input TEXT and IMAGES
    """
    width, height = tuple(unit * el for el in page_size)

    # Default frame paddings
    frameStyle = {
        'width': 3.5*inch,
        'height': 3.5*inch,
        'topPadding': 0,
        'bottomPadding': 0,
        'leftPadding': 6,
        'rightPadding': 6,
        'margin': 0.25*inch
    }

    frame_fit_row =  math.floor(width / (frameStyle['width'] + 2*frameStyle['margin']))
    frame_fit_column =  math.floor(height / (frameStyle['height'] + 2*frameStyle['margin']))
    paper_xPadding = ((width - (frame_fit_row * (frameStyle['width'] + 2*frameStyle['margin']))) / 2)
    paper_yPadding = ((height - (frame_fit_column * (frameStyle['height'] + 2*frameStyle['margin']))) / 2)

    pdf = canvas.Canvas(output, pagesize=(width, height))

    next_x = frameStyle['margin'] + paper_xPadding
    next_y = height - frameStyle['height'] - frameStyle['margin'] - paper_yPadding

    for img in images:
        if (next_x + 3.5*inch + frameStyle['margin'] > width):
            next_x = frameStyle['margin']
            next_y = next_y - 2*frameStyle['margin'] - 3.5*inch
            if (next_y < 0):
                pdf.showPage()
                next_x = frameStyle['margin'] + paper_xPadding
                next_y = height - frameStyle['height'] - frameStyle['margin'] - paper_yPadding
        pdf.drawImage(img.name, next_x , next_y , 3.5*inch, 3.5*inch)
        next_x = frameStyle['margin'] + paper_xPadding

    pdf.showPage()
    next_x = frameStyle['margin'] + paper_xPadding
    next_y = height - frameStyle['height'] - frameStyle['margin'] - paper_yPadding

    styles = getSampleStyleSheet()
    my_style = ParagraphStyle('OwnStyle', parent=styles['Title'])
    flow_obj = []

    for line in text:
        if (next_x + frameStyle['width'] + frameStyle['margin'] > width):
            next_x = frameStyle['margin'] + paper_xPadding
            next_y = next_y - 2*frameStyle['margin'] - frameStyle['height']
            if (next_y < 0):
                pdf.showPage()
                next_x = frameStyle['margin'] + paper_xPadding
                next_y = height - frameStyle['height'] - frameStyle['margin'] - paper_yPadding

        p_text = Paragraph(line, style=my_style)
        flow_obj.append(p_text)

        free_space = frameStyle['height'] - frameStyle['topPadding'] - frameStyle['bottomPadding']
        free_space -= p_text.wrap(
            frameStyle['width'] - frameStyle['leftPadding'] - frameStyle['rightPadding'] \
            + 2 * p_text.style.borderPadding, \
            frameStyle['height'] - frameStyle['topPadding'] - frameStyle['bottomPadding'])[1] \
            + p_text.style.borderPadding * 2 + 1
        free_space += p_text.style.borderPadding * 2
        frameStyle['topPadding'] = free_space / 2

        frame = Frame(next_x,
            next_y,
            frameStyle['width'],
            frameStyle['height'],
            showBoundary=1,
            topPadding=frameStyle['topPadding'],
            bottomPadding=frameStyle['bottomPadding'],
            leftPadding=frameStyle['leftPadding'],
            rightPadding=frameStyle['rightPadding'])

        frame.addFromList(flow_obj, pdf)
        frameStyle['topPadding'] = 0
        next_x = next_x + 3.5*inch + 2*frameStyle['margin']
    
    pdf.showPage()
    pdf.save()


@click.option('-o','--output', 
    type=click.File('wb'), 
    default='./test/output.pdf', 
    help='Specify the output path and filename (default is current working directory)')

@click.option('-s', '--page-size', 
    type=click.Tuple([float, float]), 
    default=(8.5, 11), 
    metavar='<width> <height>', 
    help='Specify the size of the output file')

@click.option('-I', '--use-inch', 'unit', 
    flag_value=inch, 
    default=True, 
    help='Use inches for measurement (default)')

@click.option('-M', '--use-mm', 'unit', 
    flag_value=mm, 
    help='Use millimeters for measurement')

@click.option('-p', '--page-numbers', 
    is_flag=True,
    default=False,
    help='Print the number and face of every page')

@click.option('-f', '--set-font',
    type=click.Choice([
        'Courier', 
        'Courier-Bold', 
        'Courier-BoldOblique', 
        'Courier-Oblique', 
        'Helvetica', 
        'Helvetica-Bold', 
        'Helvetica-BoldOblique', 
        'Helvetica-Oblique', 
        'Symbol', 
        'Times-Bold', 
        'Times-BoldItalic', 
        'Times-Italic', 
        'Times-Roman', 
        'ZapfDingbats']),
        default='Times-Roman',
        metavar='<font>',
        help='Sets the font of the text')

@click.option('--debug', 
    is_flag=True,
    default=False,
    help='Show the boundary for every card')


@click.argument('file',
    nargs=1,
    type=click.File('r'),
    required=False
    )

@main.command(name='from')
def generate_from_file(output, page_size, unit, file, page_numbers, debug, set_font):
    '''
    Generates the pdfstack from a given XML FILE. 
    This command uses large amounts of pictures and text messages, 
    declared and organised in the XML document, to create a multi paged PDF document.
    The front and back of the cards are organised automatically.
    
    If you dont know how to write the XML file, just run the command without any arguments. 
    This will generate a modifiable example file.
    '''
    
    import xml.etree.ElementTree as ET

    if (file == None):
        click.echo('''
        No argument of type FILE was given. Generating example file...
        You can find the example file in ./example.xml.
        For more information about the comand usage use the --help option.
        ''')

        top = ET.Element('cards')
        child_img = ET.SubElement(top, 'figure', {'path': './path/figure/front/of/card'})
        child_img.text = 'This is the text from the back of the card'
        child_text = ET.SubElement(top, 'text')
        child_text.text = 'This is the text from the front of the card'

        comment = ET.Comment('''
        Modify this file using only the two tags shown above with their available attributes. 
        Using custom tags or atributes may result in application failure.
        ''')
        top.append(comment)

        from xml.dom import minidom 
        f = open("./example.xml", "w")
        f.write((minidom.parseString(ET.tostring(top))).toprettyxml(indent="  "))   
        f.close()
        return    

    width, height = tuple(unit * el for el in page_size)
    
    tree = ET.parse(file.name)
    root = tree.getroot()

    pdf = canvas.Canvas(output, pagesize=(width, height))
    
    frames = []
    frameStyle = {
        'width': 3.5*inch,
        'height': 3.5*inch,
        'topPadding': 0,
        'bottomPadding': 0,
        'leftPadding': 0,
        'rightPadding': 0,
        'margin': 0.25*inch
    }

    styles = getSampleStyleSheet()
    my_style = ParagraphStyle('OwnStyle', parent=styles['Title'])
    my_style.leftIndent = 10
    my_style.rightIndent = 10
    my_style.fontName = set_font

    #   Centering the frame group on the paper
    frame_fit_row =  math.floor(width / (frameStyle['width'] + 2*frameStyle['margin']))
    frame_fit_column =  math.floor(height / (frameStyle['height'] + 2*frameStyle['margin']))
    paper_xPadding = ((width - (frame_fit_row * (frameStyle['width'] + 2*frameStyle['margin']))) / 2)
    paper_yPadding = ((height - (frame_fit_column * (frameStyle['height'] + 2*frameStyle['margin']))) / 2)

    next_x = frameStyle['margin'] + paper_xPadding
    next_y = height - frameStyle['height'] - frameStyle['margin'] - paper_yPadding

    maxframes_on_page = frame_fit_column * frame_fit_row

    page_index = 0
    frame_index = 0
    frame_contents = [ [] for i in range(math.ceil(len(root.getchildren())/maxframes_on_page)*2) ]
    
    
    for card in root:
        if (frame_index >= maxframes_on_page):
            page_index += 2
            frame_index = 0
        if (card.tag == 'figure'):
            frame_contents[page_index].append(Image(
                card.attrib['path'], 
                width=frameStyle['width'], 
                height=frameStyle['height'])
            )
            frame_contents[page_index+1].append(Paragraph(card.text, style=my_style))
        elif (card.tag == 'text'):
            frame_contents[page_index].append(Paragraph(card.text, style=my_style))
            frame_contents[page_index+1].append(Paragraph('empty', style=my_style))

        frame_index += 1
    
    for page in frame_contents:
        for content in page:
            if (next_x + frameStyle['width'] + frameStyle['margin'] > width):
                next_x = frameStyle['margin'] + paper_xPadding
                next_y = next_y - 2*frameStyle['margin'] - frameStyle['height']

            if (isinstance(content, Paragraph)):
                
                free_space = frameStyle['height'] - frameStyle['topPadding'] - frameStyle['bottomPadding']
                free_space -= content.wrap(
                    frameStyle['width'] - frameStyle['leftPadding'] - frameStyle['rightPadding'] \
                    + 2 * content.style.borderPadding, \
                    frameStyle['height'] - frameStyle['topPadding'] - frameStyle['bottomPadding'])[1] \
                    + content.style.borderPadding * 2 + 1
                free_space += content.style.borderPadding * 2
                frameStyle['topPadding'] = free_space / 2

            frame = Frame(
                next_x,
                next_y,
                frameStyle['width'],
                frameStyle['height'],
                showBoundary=int(debug),
                topPadding=frameStyle['topPadding'],
                bottomPadding=frameStyle['bottomPadding'],
                leftPadding=frameStyle['leftPadding'],
                rightPadding=frameStyle['rightPadding'])

            frame.addFromList([content], pdf)
            frameStyle['topPadding'] = 0

            next_x = next_x + frameStyle['width'] + 2*frameStyle['margin']
        
        if (page_numbers):
            pdf.drawCentredString(width/2, 20, str(pdf.getPageNumber()) + 
            (pdf.getPageNumber() % 2 == 0 and ' (Back)' or ' (Front)'))

        pdf.showPage()
        next_x = frameStyle['margin'] + paper_xPadding
        next_y = height - frameStyle['height'] - frameStyle['margin'] - paper_yPadding

    pdf.save()

def print_help():
    ctx = click.get_current_context()
    click.echo(ctx.get_help())
    ctx.exit()