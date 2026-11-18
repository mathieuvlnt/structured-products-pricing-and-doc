"""Independent photographic cover, prepended to existing indicative termsheets."""
from io import BytesIO
from PIL import Image as PILImage
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4
from pypdf import PdfReader, PdfWriter

BROWN=HexColor('#503B32'); TAUPE=HexColor('#866C5C'); INK=HexColor('#30343A')
PHOTO=Path(__file__).resolve().parent/'assets'/'cover_photo.jpg'
def ensure_cover_photo():
    """Use the user-selected cover bundled with the project; never fetch remotely."""
    if not PHOTO.is_file():
        raise FileNotFoundError(f"Bundled cover photograph missing: {PHOTO}")
    with PILImage.open(PHOTO) as im:
        im.verify()
    return PHOTO

TITLES={
 'Phoenix Autocall':('PHOENIX AUTOCALL','PHOENIX AUTOCALL'),
 'Athena Autocall':('ATHENA AUTOCALL','ATHENA AUTOCALL'),
 'European Option':('EUROPEAN OPTION','OPTION EUROPÉENNE'),
 'Capital Protected Note':('CAPITAL PROTECTED NOTE','NOTE À CAPITAL PROTÉGÉ'),
 'Credit Linked Note':('CREDIT LINKED NOTE','CREDIT LINKED NOTE'),
}

def add_cover(pdf_bytes, product, language='EN', photo_bytes=None):
    """Preserve body pages; use an authentic user-provided photograph or a non-photographic layout."""
    fr=language=='FR'; w,h=A4
    b=BytesIO(); c=canvas.Canvas(b,pagesize=A4)
    c.setFillColor(white);c.rect(0,0,w,h,fill=1,stroke=0)
    c.setFillColor(BROWN);c.rect(0,h-15,w,15,fill=1,stroke=0)
    c.setFillColor(BROWN);c.setFont('Helvetica-Bold',10)
    c.drawString(48, h-62, 'STRUCTURED PRODUCTS' if not fr else 'PRODUITS STRUCTURES')
    c.setFillColor(TAUPE);c.setFont('Helvetica',9)
    c.drawString(48,h-82,'INDICATIVE TERMS & CONDITIONS' if not fr else 'TERMES ET CONDITIONS INDICATIFS')
    # Use the photograph supplied by the user, bundled locally.
    photo_path=ensure_cover_photo()
    im=ImageReader(str(photo_path));iw,ih=im.getSize()
    box=(0,h-465,w,345); ratio=max(box[2]/iw,box[3]/ih)
    dw,dh=iw*ratio,ih*ratio
    c.saveState();p=c.beginPath();p.rect(*box);c.clipPath(p,stroke=0)
    c.drawImage(im,(w-dw)/2,box[1]+(box[3]-dh)/2,width=dw,height=dh,mask='auto')
    c.restoreState()
    c.setFillColor(BROWN);c.rect(48,h-502,60,4,stroke=0,fill=1)
    family=getattr(product,'family','Phoenix Autocall')
    if family not in TITLES: family='Phoenix Autocall'
    c.setFillColor(INK);c.setFont('Helvetica-Bold',21)
    c.drawString(48,h-548,TITLES[family][1 if fr else 0])
    c.setFont('Helvetica',12);c.setFillColor(TAUPE)
    underlying=getattr(product,'underlying','')
    if len(underlying)>67:underlying=underlying[:64]+'...'
    c.drawString(48,h-575,underlying)
    c.setStrokeColor(HexColor('#D9C7B2'));c.line(48,h-604,w-48,h-604)
    c.setFillColor(INK);c.setFont('Helvetica',10)
    c.setFillColor(BROWN);c.setFont('Helvetica-Bold',9)
    c.drawString(48,112,'ILLUSTRATIVE DOCUMENT  •  NOT AN OFFER' if not fr else 'DOCUMENT ILLUSTRATIF  •  NE CONSTITUE PAS UNE OFFRE')
    c.setFillColor(TAUPE);c.setFont('Helvetica',8)
    c.drawString(48,94,'Independent prototype. Not issued or approved by any financial institution.' if not fr else 'Prototype indépendant. Non émis ni approuvé par un établissement financier.')
    c.setStrokeColor(HexColor('#D9C7B2'));c.line(48,69,w-48,69)
    c.setFont('Helvetica',8);c.drawString(48,51,'STRUCTURED PRODUCTS  /  PRICING & DOCUMENTATION'  if not fr else 'PRODUITS STRUCTURES')
    c.showPage();c.save();b.seek(0)
    writer=PdfWriter();writer.add_page(PdfReader(b).pages[0]);writer.append(PdfReader(BytesIO(pdf_bytes)))
    out=BytesIO();writer.write(out);return out.getvalue()
