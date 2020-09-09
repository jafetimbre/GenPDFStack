from reportlab.platypus import Flowable, Paragraph, Image

class Card(Flowable):
    def __init__(self, width, height=100):
        Flowable.__init__(self)
        self.width = width
        self.height = height
    #----------------------------------------------------------------------
    def __repr__(self):
        return "Line(w=%s)" % self.width
    #----------------------------------------------------------------------
    def draw(self):
        """
        draw the line
        """
        self.canv.rect(0,0,100,100)