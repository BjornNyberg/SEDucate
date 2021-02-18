import numpy as np
import pandas as pd
import random,os
from PIL import Image, ImageFont, ImageDraw, ImageOps

def createLog(probMatrix,paleoMap,logTemp,logLegend,path,outDir,cNum,fNum,lNum):
    depImg = Image.open(paleoMap)
    
    chance = pd.read_excel(probMatrix,index_col=0)
    chance = chance.div(100.0).transpose()
    
    colors = set([])
    for pixel in depImg.getdata():
        colors.update([pixel])
    colors = list(colors)  

    sEnv = {colors[0]:'delta',colors[1]:'floodplain',colors[2]:'shoreface',colors[3]:'channel'}
    
    wV,hV = depImg.size
    w,h = int(wV*0.9),int(hV*0.9)
    for n3 in range(cNum):
        images = []
        locations = []
        mW, lW = 0,0
        depImg = Image.open(paleoMap)
        for n in range(lNum):
            curW,curHeight = 0,0
            wR,hR = random.randrange(0,w),random.randrange(0,h)
            locations.append([wR,hR])
            
            for n2 in range(fNum):
                if n2 == 0:
                    try:
                        curEnv = sEnv[depImg.load()[wR,hR]]
                        env = curEnv

                    except Exception:
                        print('Error - Color not found in sEnv dictionary. Paleogeography image contains %s classes and each class requires a matching depositional environment/facies/facies association in the sEnv dictionary variable.'%(len(colors)))
                        break
                    
                    options = chance[curEnv]
                    keys = list(options.index)
                    probs = list(options)
                else:
                    choice = np.random.choice(keys, 1,  p=probs)
                    env = choice[0]
                curPath = os.path.join(path,env)
                fnames = os.listdir(curPath)

                if len(fnames) == 0:
                    print('Error - No images found in directory %s' %(curPath))
                    break
                  
                img = Image.open(os.path.join(curPath,random.choice(fnames)))
                width,height = img.size
                bbox = (0, 0, width, int(height-2))
                img = img.crop(bbox)
                images.append(img)          
                curHeight += height
                if width > curW:
                    curW = width
                if curHeight > lW:
                    lW = curHeight
                mW += curW
            
        lW += 500
        new_im = Image.new('RGB', size=(3000, lW),color=(255,255,255,0))
        new_im2 = Image.new('RGB', size=(3000, lW),color=(255,255,255,0))
    
        x_offset, curWidth = 0,0
        y_offset = lW
        n = 1
        logImg = Image.open(logTemp)
        y_offset-=250
        new_im.paste(logImg, (int(x_offset),y_offset))
        new_im2.paste(logImg, (int(x_offset)+65,y_offset))
        font = ImageFont.truetype('arial.ttf',50)
        draw = ImageDraw.Draw(new_im)   
        draw2 = ImageDraw.Draw(new_im2)  
        c = 1
        draw.text((int(x_offset)+350,y_offset),'log #%s'%(c),(0,0,0),font=font)
        draw2.text((int(x_offset)+415,y_offset),'log #%s'%(c),(0,0,0),font=font)
        for enum,im in enumerate(images):
          if enum % fNum == 0 and enum != 0:
              c += 1
              y_offset = lW
              x_offset += 600
              n += 1
              logImg = Image.open(logTemp)
              y_offset-=250
              new_im.paste(logImg, (int(x_offset),y_offset))
              new_im2.paste(logImg, (int(x_offset)+65,y_offset))
              draw.text((int(x_offset)+350,y_offset),'log #%s'%(c),(0,0,0),font=font)
              draw2.text((int(x_offset)+415,y_offset),'log #%s'%(c),(0,0,0),font=font)
          
          y_offset -= im.size[1]
    
          new_im2.paste(im, (int(x_offset),int(y_offset)))
          width,height = im.size
    
          bbox = (65, 0, width, height)
          im = im.crop(bbox)
          new_im.paste(im, (int(x_offset),int(y_offset)))
          curWidth += width
        
        image = Image.new('RGB', (wV, hV),color=(255,255,255,0))
        
        draw3 = ImageDraw.Draw(depImg)
        draw4 = ImageDraw.Draw(image)
        font = ImageFont.truetype('arial.ttf',100)
        for enum,loc in enumerate(locations):
            draw3.text((loc[0],loc[1]),str(enum+1),(255,255,255),font=font)
            draw4.text((loc[0],loc[1]),str(enum+1),(0,0,0),font=font)
        
        image = ImageOps.expand(image, border=10)
        depImg = ImageOps.expand(depImg, border=10)
        
        logImg = Image.open(logLegend)
        y_offset = 100
        x_offset += 600
        new_im.paste(logImg, (int(x_offset),y_offset))
        new_im2.paste(logImg, (int(x_offset)+65,y_offset))
        
        new_im.save(r'%s\candidate_%s.pdf'%(outDir,n3+1))
        new_im2.save(r'%s\candidate_answers_%s.pdf'%(outDir,n3+1))
        depImg.save(r'%s\PaleoMap_answers_%s.jpg'%(outDir,n3+1))
        image.save(r'%s\PaleoMap_%s.jpg'%(outDir,n3+1))

if __name__ == "__main__":
    '''Input parameters for the sEducate scripts. Replace each parameter with the absolute path for your working directory'''
    dirname = os.path.dirname(__file__) # directory to scripts
    dirImages = os.path.join(dirname,'Images') #folders containing images of facies or facies associations 
    
    probMatrix = os.path.join(dirname,'probabilityMatrix.xlsx') #excel file containing probability matrix 
    paleoMap = os.path.join(dirname,'maps\map.png') #image file containg the paleogeographic map
    log = os.path.join(dirname,'Log Templates\LogTemplate.jpg') #image file containing log template
    legend = os.path.join(dirname,'Log Templates\legend.jpg') #image file containing log template
    outDir = os.path.join(dirname,'Outputs') # output directory
    
    cNum = 15 # Number of candidates
    fNum = 3 # Number of facies/facies associations per log
    lNum = 3 # Number of logs per candidate
    createLog(probMatrix,paleoMap,log,legend,dirImages,outDir,cNum,fNum,lNum)
    