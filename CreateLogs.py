import numpy as np
import random,os
import pandas as pd
from PIL import Image, ImageFont, ImageDraw

def createLog(probMatrix,logTemp,logLegend,path,outDir,cNum,fNum,lNum):
    
    chance = pd.read_excel(probMatrix,index_col=0)
    chance = chance.div(100.0).transpose()
    font = ImageFont.truetype('arial.ttf',50)
    
    for n3 in range(cNum):
        images = []
        mW, lW = 0,0
             
        for n in range(lNum):
            curW,curHeight = 0,0  
            
            for n2 in range(fNum):
                if n2 == 0:
                    curEnv = random.choice(list(chance.keys()))
                    env = curEnv
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
        
        draw = ImageDraw.Draw(new_im)   
        draw2 = ImageDraw.Draw(new_im2)  
        c = 1
        draw.text((int(x_offset)+400,y_offset),'log #%s'%(c),(0,0,0),font=font)
        draw2.text((int(x_offset)+465,y_offset),'log #%s'%(c),(0,0,0),font=font)
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
              draw.text((int(x_offset)+400,y_offset),'log #%s'%(c),(0,0,0),font=font)
              draw2.text((int(x_offset)+465,y_offset),'log #%s'%(c),(0,0,0),font=font)
          
          y_offset -= im.size[1]
    
          new_im2.paste(im, (int(x_offset),int(y_offset)))
          width,height = im.size
    
          bbox = (65, 0, width, height)
          im = im.crop(bbox)
          new_im.paste(im, (int(x_offset),int(y_offset)))
          curWidth += width
            
        logImg = Image.open(logLegend)
        y_offset = 100
        x_offset += 600
        new_im.paste(logImg, (int(x_offset),y_offset))
        new_im2.paste(logImg, (int(x_offset)+65,y_offset))
        
        new_im.save(r'%s\candidate_%s.pdf'%(outDir,n3+1))
        new_im2.save(r'%s\candidate_answers_%s.pdf'%(outDir,n3+1))

if __name__ == "__main__":
    '''Input parameters for the sEducate scripts. Replace each parameter with the absolute path for your working directory'''
    dirname = os.path.dirname(__file__) # directory to scripts
    dirImages = os.path.join(dirname,'Images') #folders containing images of facies or facies associations 

    probMatrix = os.path.join(dirname,'probabilityMatrix.xlsx') #excel file containing probability matrix 
    log = os.path.join(dirname,'Log Templates\LogTemplate.jpg') #image file containing log template
    legend = os.path.join(dirname,'Log Templates\legend.jpg') #image file containing log template
    outDir = os.path.join(dirname,'Outputs') # output directory

    cNum = 2 # Number of candidates
    fNum = 3 # Number of facies/facies associations per log
    lNum = 3 # Number of logs per candidate
    createLog(probMatrix,log,legend,dirImages,outDir,cNum,fNum,lNum)