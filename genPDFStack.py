import click
import math
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, inch
from reportlab.platypus import Image, Frame, Paragraph, SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import xml.etree.ElementTree as ET
from Tags import Tags 


@click.option('-s', '--page-size', 
    type=click.Tuple([float, float]), 
    default=(0, 0),
    metavar='<width> <height>', 
    help='Specify the size of the output file')

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

@click.option('--debug', 
    is_flag=True,
    default=False,
    help='Show debug information')

@click.option('-H', '--h-cut-lines',
    is_flag=True,
    default=False,
    help='Show horizontal cut lines at the marins')

@click.option('-V', '--v-cut-lines',
    is_flag=True,
    default=False,
    help='Show vertical cut lines at the marins')


@click.argument('file',
    nargs=1,
    type=click.File('r'),
    required=False)

@click.command()

def main(file, output, page_size, unit, debug, h_cut_lines, v_cut_lines):
    '''
    Generates the pdfstack from a given XML FILE. 
    This command uses large amounts of pictures and text messages, 
    declared and organised in the XML document, to create a multi paged PDF document.
    The front and back of the cards are organised automatically.
    
    If you dont know how to write the XML file, just run the command without any arguments. 
    This will generate a modifiable example file.
    '''
    pdfmetrics.registerFont(TTFont('Varta-Bold', r'lib\fonts\Varta-Bold.ttf'))
    pdfmetrics.registerFont(TTFont('Varta-Light', r'lib\fonts\Varta-Light.ttf'))
    pdfmetrics.registerFont(TTFont('Varta-Regular', r'lib\fonts\Varta-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('Varta-SemiBold', r'lib\fonts\Varta-SemiBold.ttf'))

    # Some default values
    DEFAULTS = {
        'width': 8.5*unit,
        'height': 11*unit,
        'font': 'Varta-Regular',
        'font-size': 21,
    }

    if (file == None):
        print('No file given')
        return

    tree = ET.parse(file.name)
    root = tree.getroot()

    # Parsing the xml file
    page_config = root.find(Tags.PAGECONFIG.value)
    if (page_config):
        for element in page_config:
            if (element.tag == Tags.PAGEWIDTH.value):
                if (is_float(element.text)):
                    DEFAULTS['width'] = float(element.text)*unit

            elif (element.tag == Tags.PAGEHEIGHT.value):
                if (is_float(element.text)):
                    DEFAULTS['height'] = float(element.text)*unit

            elif (element.tag == Tags.FONT.value):   
                DEFAULTS['font'] = element.text

            elif (element.tag == Tags.FONTSIZE.value):
                if (is_float(element.text)):
                    DEFAULTS['font-size'] = float(element.text)
            
    if (page_size != (0, 0)):
        DEFAULTS['width'], DEFAULTS['height'] = tuple(unit * el for el in page_size)

    pdf = canvas.Canvas(output, pagesize=(DEFAULTS['width'], DEFAULTS['height']))
    
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
    my_style.fontName = DEFAULTS['font']
    my_style.fontSize = DEFAULTS['font-size']

    #   Centering the frame group on the paper
    frame_fit_row =  math.floor(DEFAULTS['width'] / (frameStyle['width'] + 2*frameStyle['margin']))
    frame_fit_column =  math.floor(DEFAULTS['height'] / (frameStyle['height'] + 2*frameStyle['margin']))
    paper_xPadding = ((DEFAULTS['width'] - (frame_fit_row * (frameStyle['width'] + 2*frameStyle['margin']))) / 2)
    paper_yPadding = ((DEFAULTS['height'] - (frame_fit_column * (frameStyle['height'] + 2*frameStyle['margin']))) / 2)

    next_x = frameStyle['margin'] + paper_xPadding
    next_y = DEFAULTS['height'] - frameStyle['height'] - frameStyle['margin'] - paper_yPadding

    maxframes_on_page = frame_fit_column * frame_fit_row
    if (maxframes_on_page <= 0):
        click.echo('Cannot fit frames on page with given dimensions')
        return
    
    page_index = 0
    frame_index = 0

    page_content = root.find(Tags.CONTENT.value)
    if (page_content):
        page_cards = page_content.findall(Tags.CARD.value)
        if (page_cards):
            frame_contents = [ [] for i in range(math.ceil(len(page_cards)/maxframes_on_page)*2) ]
            for card in page_cards:
                if (frame_index >= maxframes_on_page):
                    page_index += 2
                    frame_index = 0

                card_content = card.getchildren()

                if (len(card_content) == 0):
                    frame_contents[page_index].append(None)
                    frame_contents[page_index+1].append(None)

                elif (len(card_content) > 0):
                    index = 0
                    for element in card_content:
                        if (element.tag == Tags.TEXT.value):
                            # TODO: Some error handleing with the text and missing attrib
                            text = element.attrib.get('text', None)
                            if (text == None):
                                click.echo('Error on TEXT attribute (TEXT) at card ' + str(page_cards.index(card)+1))
                                return
                            frame_contents[page_index+index].append(Paragraph(text, style=my_style))
                        
                        elif (element.tag == Tags.IMAGE.value):
                            # TODO: Some error handleing with the path and missing attrib
                            file_path = element.attrib.get('path', None)
                            if (file_path == None):
                                click.echo('Error on PATH attribute (IMAGE) at card ' + str(page_cards.index(card)+1))
                                return

                            import os.path
                            from os import path
                            if (os.path.isfile(file_path) == False):
                                click.echo('Invalid path <' + file_path + '> (IMAGE) at card ' + str(page_cards.index(card)+1))
                                return

                            frame_contents[page_index+index].append(Image(
                                file_path, 
                                width=frameStyle['width'], 
                                height=frameStyle['height']))

                        index += 1
                        if (index >= 2): break

                    if (index == 1):
                        frame_contents[page_index+1].append(None)

                frame_index += 1
    
            for page in frame_contents:
                for content in page:
                    if (next_x + frameStyle['width'] + frameStyle['margin'] > DEFAULTS['width']):
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

                    if (content == None):
                        frame.addFromList([], pdf)
                    else:
                        frame.addFromList([content], pdf)

                    frameStyle['topPadding'] = 0

                    next_x = next_x + frameStyle['width'] + 2*frameStyle['margin']
                
                if (debug):
                    pdf.drawCentredString(DEFAULTS['width']/2, 20, str(pdf.getPageNumber()) + 
                    (pdf.getPageNumber() % 2 == 0 and ' (Back)' or ' (Front)'))

                if (v_cut_lines):
                    # cut line length
                    line_length = paper_yPadding-5
                    pdf.setLineWidth(0.1)

                    # vertical cut lines
                    next_line = paper_xPadding
                    for i in range(0, frame_fit_row+1):
                        pdf.line(next_line, 0, next_line, line_length)
                        pdf.line(next_line, DEFAULTS['height'], next_line, DEFAULTS['height']-line_length)
                        next_line += frameStyle['margin']*2 + frameStyle['width']
                if (h_cut_lines):
                    # cut line length
                    line_length = paper_xPadding-5
                    pdf.setLineWidth(0.1)

                    # horizontal cut lines
                    next_line = paper_yPadding
                    for i in range(0, frame_fit_column+1):
                        pdf.line(0, next_line, line_length, next_line)
                        pdf.line(DEFAULTS['width'], next_line, DEFAULTS['width']-line_length, next_line)
                        next_line += frameStyle['margin']*2 + frameStyle['width']

                pdf.showPage()
                next_x = frameStyle['margin'] + paper_xPadding
                next_y = DEFAULTS['height'] - frameStyle['height'] - frameStyle['margin'] - paper_yPadding
    pdf.save()


def is_float(value):
  try:
    float(value)
    return True
  except:
    return False

def print_help():
    ctx = click.get_current_context()
    click.echo(ctx.get_help())
    ctx.exit()