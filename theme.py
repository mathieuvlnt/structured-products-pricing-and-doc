"""Independent institutional brown design system (not J.P. Morgan branding)."""
from reportlab.lib import colors
from reportlab.lib.units import mm
from datetime import date
BROWN=colors.HexColor('#503B32')
TAUPE=colors.HexColor('#866C5C')
SAND=colors.HexColor('#D9C7B2')
IVORY=colors.HexColor('#F4F0EB')
CHARCOAL=colors.HexColor('#30343A')
GRID=colors.HexColor('#D8CDC2')
WHITE=colors.white

def page_chrome(canvas, doc, language='EN', total=None, left=17*mm, right=17*mm):
    canvas.saveState()
    w,h=doc.pagesize
    canvas.setFillColor(BROWN)
    canvas.rect(0,h-8*mm,w,8*mm,stroke=0,fill=1)
    canvas.setFillColor(IVORY)
    canvas.setFont('Helvetica-Bold',8)
    canvas.drawString(left,h-5.7*mm,'STRUCTURED PRODUCTS  /  INDICATIVE TERMS' if language=='EN' else 'PRODUITS STRUCTURÉS  /  CONDITIONS INDICATIVES')
    canvas.setFillColor(TAUPE)
    canvas.setFont('Helvetica',7)
    canvas.drawRightString(w-right,h-13.5*mm,date.today().strftime('%d %b %Y'))
    canvas.setStrokeColor(SAND)
    canvas.setLineWidth(.65)
    canvas.line(left,16*mm,w-right,16*mm)
    canvas.setFillColor(TAUPE)
    canvas.setFont('Helvetica',6.5)
    #if doc.page > 1:
    canvas.drawString(left, 11.5*mm,
        'PROTOTYPE' if language == 'EN' else 'PROTOTYPE')
    page = f'{doc.page + 1:02d}' + (f' / {total + 1:02d}' if total else '')
    canvas.drawRightString(w-right,11.5*mm,page)
    canvas.restoreState()
