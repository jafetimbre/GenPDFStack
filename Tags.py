from enum import Enum

class Tags(Enum):
    # Main, root tag
    MAIN = 'main'
    
    # Page configuration tags
    PAGECONFIG = 'pageConfig'
    PAGEWIDTH = 'pageWidth'
    PAGEHEIGHT = 'pageHeight'
    FONT = 'font'
    FONTSIZE = 'fontSize'

    # Content tags
    CONTENT = 'content'
    CARD = 'card'
    IMAGE = 'image'
    TEXT = 'text'
