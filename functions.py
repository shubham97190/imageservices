import requests
import textwrap
from io import BytesIO
from base64 import b64decode
from PIL import Image,ImageDraw,ImageFont

from django.conf import settings

def convertInchTOPixel(self,*args):
    """ Convert image size inch to pixel """
    return list(map(lambda x : int(x * 96),args))
    
def urlToImage(url):
    """ download the image, convert it to a Pillow , and then read it into pillow format  """

    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    return image

def fillBackgroundImage(backgroundImage,image):
    """ Fill Ractangle with Background Image """
    width, height = image.size
    backgroundWidth, backgroundHeight = backgroundImage.size
    blankImage = Image.new('RGB', (width,height), (128,128,128))
    
    for i in range(0, width, backgroundWidth):
        for j in range(0, height, backgroundHeight):
            blankImage.paste(backgroundImage, (i, j))
    return blankImage

def currentSiteURL(request):
    """Returns fully qualified URL (no trailing slash) for the current site."""
    from django.contrib.sites.shortcuts import get_current_site

    current_site = get_current_site(request)
    protocol = getattr(settings, 'MY_SITE_PROTOCOL', 'https')
    port = getattr(settings, 'MY_SITE_PORT', '')
    url = '%s://%s' % (protocol, current_site.domain)
    if port:
        url += ':%s' % port
    return url

def convertdataTOimage(data):
    """ Convert Data to image formate """
    data = data.partition(",")[2]
    padding = len(data)%4
    data += "="*padding
    image = Image.open(BytesIO(b64decode(data)))
    return image

def breakFix(text, width, font):
    '''
    Break multiline text on image
    '''
    if not text:
        return
    low = 0
    high = len(text)

    while low < high:

        middle = (low + high + 1) // 2
        splitText = text[:middle]
        textWidth, textHeight = font.getsize(splitText)

        if textWidth <= width:
            low = middle
        else:
            high = middle - 1

    splitText = text[:low]

    return splitText

def drawMultipleLineText(img, text, color,stick_width=None,mat_width=None):
    '''
    PIL Draw multiline text on image
    '''

    width = img.size[0]
    height = img.size[1]
    fontSize = int(2*(width/96+height/96))
    font = ImageFont.truetype("imageservice/static/fonts/Roboto-Thin.ttf",fontSize)

    if mat_width:
        width = mat_width
    elif stick_width:
        width = width - (2*stick_width)

    textDraw = ImageDraw.Draw(img)
    splitText = breakFix(text, width, font)
    splitTextLength = len(splitText)

    if splitTextLength <= 4:
        splitTextLength = 1
    
    lines = textwrap.wrap(text, width=splitTextLength,drop_whitespace=False)
    height = sum(font.getsize(p)[1] for p in lines)

    if height > img.size[1]:
        raise ValueError("text doesn't fit")

    y_text = (img.size[1] - height) // 2
    
    for line in lines:
        line_width, line_height = font.getsize(line)
        textDraw.text(((img.size[0] - line_width) / 2, y_text),line, font=font, fill=color)
        y_text += line_height
   