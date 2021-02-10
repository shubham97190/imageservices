import os.path
from math import ceil
from secrets import token_hex
from PIL import Image,ImageOps,ImageFile

# Create your views here.
from django.conf import settings
from rest_framework import views
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from .serializers import GetImageSerializer

from functions import *


BACKGROUND_URL = r'https://quickartframe.24livehost.com/wp-content/uploads/mat-colors/'
IMAGE_URL = r'https://quickartframe.24livehost.com/wp-content/uploads/frame-sticks/'

ImageFile.LOAD_TRUNCATED_IMAGES = True

class GetImageView(views.APIView):

    """
    A view that can accept POST requests with JSON content.
    """
    parser_classes = [JSONParser]
   
    def post(self, request, format=None):

        if len(request.data) == 0:
            return Response({'message':'Images not found','status':404})

        topMatFrameWidth = topMatFrameHeight=0
        middleMatFrameWidth = middleMatFrameHeight=0
        bottomMatFrameWidth = bottomMatFrameHeight=0
        finalStickImage = bottomFabricSku = topFabricSku = ''

        centerText = "UPLOAD IMAGE TO SEE IT FRAME"

        """ Get Width and Height """
        frameGlassWidth = float(request.data['parts']['frame']['width'])
        frameGlassHeight = float(request.data['parts']['frame']['height'])
        """ End """

        fontSize = int(2*(frameGlassWidth+frameGlassHeight))

        """ Code to resize Stick image to use further in the system """
        stickLengthToResize = int(frameGlassWidth*96)
        if frameGlassWidth < frameGlassHeight:
            stickLengthToResize = int(frameGlassHeight*96)
        """ Code to resize Stick image to use further in the system end """  

        if 'product_id' in request.data['parts']['frame']:
            """ Get Product ID"""
            productID = request.data['parts']['frame']['product_id']

            """ Code to open and resize Stick Image object """
            try:
                finalStickImage = urlToImage(IMAGE_URL+str(productID)+'-stick.png')
            except IOError:
                return Response({'message':'Images not found','status':404})

            """ Get Bottom Mat  """
            if 'bottom_mat' in request.data['parts'] :

                bottomFabricSku = request.data['parts']['bottom_mat']['fabric_sku']
                bottomMat = float(request.data['parts']['bottom_mat']['border']['top'])
                bottomMatAllside = bottomMat *2
                bottomMatFrameWidth, bottomMatFrameHeight = convertInchTOPixel(self,frameGlassWidth-bottomMatAllside,frameGlassHeight-bottomMatAllside)
                bottomMatFrameWidth = bottomMatFrameWidth-finalStickImage.size[1]
                bottomMatFrameHeight = bottomMatFrameHeight-finalStickImage.size[1]

            """ End """

            """ Get Top Mat  """
            if 'top_mat' in request.data['parts']:

                topFabricSku = request.data['parts']['top_mat']['fabric_sku']
                topMat = float(request.data['parts']['top_mat']['border']['top'])
                topMatAllside = topMat *2
                topMatFrameWidth, topMatFrameHeight = convertInchTOPixel(self,frameGlassWidth-topMatAllside,frameGlassHeight-topMatAllside)
                topMatFrameWidth = topMatFrameWidth-finalStickImage.size[1]
                topMatFrameHeight = topMatFrameHeight-finalStickImage.size[1]

            """ End """
            frameGlassWidth, frameGlassHeight = convertInchTOPixel(self,frameGlassWidth,frameGlassHeight) # Convert image size inch to pixel
           
            """ Code to add thickness in Height and  width"""

            if 'top_mat' in request.data['parts']:

                frameGlassWidth, frameGlassHeight = frameGlassWidth+finalStickImage.size[1], frameGlassHeight+finalStickImage.size[1]
                stickLengthToResize = stickLengthToResize+finalStickImage.size[1]

            """ Code to create final Stick Image object """

            if finalStickImage.size[0] < stickLengthToResize:

                blankResizeImage = Image.new('RGBA', (stickLengthToResize,finalStickImage.size[1]), (0,0,0,0))
                finalStickImageCrop = finalStickImage.crop((finalStickImage.size[1],0,finalStickImage.size[0],finalStickImage.size[1]))  
                count =  ceil(stickLengthToResize/finalStickImage.size[0])
                
                for cnt in range(count-1,-1,-1):
                    pasteImageXPosition = cnt*finalStickImageCrop.size[0]
                    blankResizeImage.paste(finalStickImage,(pasteImageXPosition,0))
                finalStickImage = blankResizeImage  

            """ End Code to create final Stick Image object """

            """ Code to rotate finalStickImage together with corner in all directions """

            angle = -270

            leftStick = finalStickImage.rotate(angle,expand=True)
            bottomStick = leftStick.rotate(angle,expand=True)
            rightStick = bottomStick.rotate(angle,expand=True)
            topStick = rightStick.rotate(angle,expand=True)

            """ End code to rotate finalStickImage together with corner in all directions """
            
            """ Crop final stick image with frameGlass width """
            cropSizeBottom = bottomStick.size[0]-frameGlassWidth
            cropSizeLeft = leftStick.size[1]-frameGlassHeight

            topStickCrop=topStick.crop((0,0,frameGlassWidth,topStick.size[1]))
            bottomStickCrop=bottomStick.crop((cropSizeBottom,0,bottomStick.size[0],bottomStick.size[1]))        
            rightStickCrop=rightStick.crop((0,0,rightStick.size[0],frameGlassHeight))       
            leftStickCrop=leftStick.crop((0,cropSizeLeft,leftStick.size[0],leftStick.size[1]))

            """ End Crop final stick image with frameGlass width """

            rightConnerStick = rightStickCrop.crop((0,0,rightStickCrop.size[0],rightStickCrop.size[0]))# Cut Right Image conner 
            blankImage = Image.new('RGB', (frameGlassWidth,frameGlassHeight), (255,255,255)) #Create Blank Image 

            

            """ Fill Ractangle with Background Image """
            if 'top_mat' in request.data['parts'] : 

                backgroundImage = urlToImage(BACKGROUND_URL+topFabricSku+'-color.png')
                blankImage = fillBackgroundImage(backgroundImage,blankImage)
        
            """ End Fill Ractangle with Background Image """ 
            
            if 'bottom_mat' in request.data['parts'] : 

                backgroundImage = urlToImage(BACKGROUND_URL+bottomFabricSku+'-color.png')
                bottomMatBlankImage = Image.new('RGB', (bottomMatFrameWidth,bottomMatFrameHeight), (255,0,255))
                bottomMatBlankImage = fillBackgroundImage(backgroundImage,bottomMatBlankImage)
                bottomMatBlankImage = ImageOps.expand(bottomMatBlankImage, border=2, fill=(204, 204, 204))
                blankImage.paste(bottomMatBlankImage, ((blankImage.size[0]-bottomMatBlankImage.size[0])//2,(blankImage.size[1]-bottomMatBlankImage.size[1])//2))
            
            if 'top_mat' in request.data['parts'] : 
                
                topMatBlankImage = Image.new('RGB', (topMatFrameWidth,topMatFrameHeight), (255,255,255))
                topMatBlankImage = ImageOps.expand(topMatBlankImage, border=2, fill=(204, 204, 204))
                blankImage.paste(topMatBlankImage, ((blankImage.size[0]-topMatBlankImage.size[0])//2,(blankImage.size[1]-topMatBlankImage.size[1])//2))

            
            """ Create Ractangle with frameglasswith """

            blankImage.paste(rightStickCrop, (topStickCrop.size[0]-topStickCrop.size[1],0),mask=rightStickCrop)
            blankImage.paste(bottomStickCrop, (0,leftStickCrop.size[1]-leftStickCrop.size[0]),mask=bottomStickCrop)
            blankImage.paste(leftStickCrop, (0,0), mask=leftStickCrop)
            blankImage.paste(topStickCrop, (0,0), mask=topStickCrop)
            blankImage.paste(rightConnerStick, (topStickCrop.size[0]-topStickCrop.size[1],0),mask=rightConnerStick)

            """ End  Create Ractangle with frameglasswith """
            if 'user_image' in request.data['parts'] : 

                imageData = request.data['parts']['user_image']['image_data'] 
                centerImage = convertdataTOimage(imageData)
                resizeCenterImage = (frameGlassWidth-(2*finalStickImage.size[1]),frameGlassHeight-(2*finalStickImage.size[1]))

                if 'top_mat' in request.data['parts']:
                    resizeCenterImage = (topMatFrameWidth, topMatFrameHeight)
                    
                elif 'bottom_mat' in request.data['parts'] :
                    resizeCenterImage = (bottomMatFrameWidth, bottomMatFrameHeight)

                centerImage = centerImage.resize(resizeCenterImage)
                blankImage.paste(centerImage, ((blankImage.size[0]-centerImage.size[0])//2,(blankImage.size[1]-centerImage.size[1])//2))

            else:
                """ Add Text on middle white area """ 

                if 'top_mat' in request.data['parts']:
                    drawMultipleLineText(blankImage, centerText, 'gray', mat_width=topMatFrameWidth)
                else:
                    drawMultipleLineText(blankImage, centerText, 'gray', stick_width=finalStickImage.size[1])

        else:
            if 'user_image' not in request.data['parts']:
                return Response({'message':'Images not found','status':404})

            imageData = request.data['parts']['user_image']['image_data']
            centerImage = convertdataTOimage(imageData)

            if 'additional_border' in request.data['parts']['frame']:

                additionalBorder = float(request.data['parts']['frame']['additional_border'])
                additionalBorder = additionalBorder*2
                additionalBorderWidth, additionalBorderHeight = convertInchTOPixel(self,frameGlassWidth-additionalBorder,frameGlassHeight-additionalBorder)
               
                frameGlassWidth, frameGlassHeight = convertInchTOPixel(self,frameGlassWidth,frameGlassHeight)
                blankImage = Image.new('RGB', (frameGlassWidth,frameGlassHeight), (255,255,255))
                blankImage = ImageOps.expand(blankImage, border=2, fill=(204, 204, 204))
                resizeCenterImage = (additionalBorderWidth,additionalBorderHeight)
                centerImage = centerImage.resize(resizeCenterImage)
                blankImage.paste(centerImage, ((blankImage.size[0]-centerImage.size[0])//2,(blankImage.size[1]-centerImage.size[1])//2),mask=centerImage)
            else:

                frameGlassWidth, frameGlassHeight = convertInchTOPixel(self,frameGlassWidth,frameGlassHeight)
                blankImage = Image.new('RGBA', (frameGlassWidth,frameGlassHeight), (0,0,0,0))
                blankImage = ImageOps.expand(blankImage, border=2, fill=(204, 204, 204))
                resizeCenterImage = (frameGlassWidth,frameGlassHeight)
                centerImage = centerImage.resize(resizeCenterImage)
                blankImage.paste(centerImage, ((blankImage.size[0]-centerImage.size[0])//2,(blankImage.size[1]-centerImage.size[1])//2),mask=centerImage)
        
        
        image_name = token_hex(16)

        if stickLengthToResize > 500:
            pass
            blankImage.thumbnail((500,500), Image.ANTIALIAS)
        blankImage.save(os.path.join(settings.BASE_DIR, "imageservice/static/images")+'/'+str(image_name)+'.png', format="png")
        file_path = currentSiteURL(request)+'/static'+'/'+str(image_name)+'.png'
        yourdata= [{
            "image": file_path,
            
        }]
        results = GetImageSerializer(yourdata, many=True).data
        return Response(yourdata)

class RemoveImageView(views.APIView):
    """
    A view that can accept POST requests with JSON content.
    """
    def post(self, request, format=None):

        if len(request.data) == 0:
            return Response({'Error':'Image Not Found'})

        imageURL = request.data['image_url']
        imagePath = imageURL.replace(currentSiteURL(request)+'/static',settings.STATICFILES_DIRS[1])
        if os.path.exists(imagePath):
            os.remove(imagePath)
            return Response({'message':'Images has been removed successfully','status':200})

        return Response({'message':'Images not found','status':404})