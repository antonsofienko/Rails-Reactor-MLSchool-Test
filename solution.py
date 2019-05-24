from argparse import ArgumentParser

from os import listdir
from os.path import isfile, join

from PIL import Image
import numpy as np

parser = ArgumentParser()
parser.add_argument("--path", dest="path",
                    help="folder with images",required=True)


parser.add_argument("--so", dest="sensitivity_other",
                    help="value of sensitivity to detect where  similar and modified pictures among others. Default 90",required=False,type=int, default=90 )

parser.add_argument("--sm", dest="sensitivity_modification",
                    help="value of sensitivity to detect  where modified images among similar. Default 20  ",required=False,type=int, default=20 )                    
args = parser.parse_args()



def load_images():
    allFiles = [f for f in listdir(args.path) if isfile(join(args.path, f))]

    name_imgArr_list  = list()

    for imagePath in allFiles:
        try:
            img = Image.open(imagePath).resize((512, 512))

            name_imgArr_list.append((imagePath,np.array(img)))
        except IOError:
            print(f"File {imagePath} can`t be opened")

    return name_imgArr_list


def calculate_mse(v1,v2):return ((v1 - v2)**2).mean(axis=None)

SS = 50#side of squeare
def left_top(image):return np.copy(image)[0:SS , 0:SS ,]
def right_button(image):return np.copy(image)[:-SS , :-SS ,]
def left_button(image):return np.copy(image)[0:SS, 0:SS ,]
def right_top(image):return np.copy(image)[:SS , :-SS ,]



def main():
    '''
        How it works:
            We  cut  from each corner of image patch(squares) 50x50 pixels, do the same for other image and calculate MSE between relative squares
            if MSE for each corner is the 0,  then images are duplicate
            if Max of 4 MSE  less then some value then images are similar

            and for understand where modified and where simililar:
            I suppose that intensity of filter is the same for all part of the image,  so MSE should be close  for all corners

            I choose corners to datect if scene from another angle             
    '''
    name_imgArr_list  = load_images()

    for i1,(k,v) in enumerate(name_imgArr_list):#
        for i2,(k2,v2) in enumerate(name_imgArr_list):

            if(k!=k2):

                diff_list = [calculate_mse(left_top(v), left_top(v2))
                            ,calculate_mse(right_button(v),right_button(v2))
                            ,calculate_mse(left_button(v), left_button(v2))
                            ,calculate_mse(right_top(v), right_top(v2))]

                max_MSE = max(diff_list)
                if all(x==0.0 for x in diff_list) and (Image.open(k).size == Image.open(k2).size):
                    del name_imgArr_list[i2]
                    print(f"same {k} and {k2}")
                    
                elif(max_MSE < args.sensitivity_other ):
                    del name_imgArr_list[i2]
                    if max_MSE  - min(diff_list) < args.sensitivity_modification:
                        print(f"modification {k} and {k2}")
                    else:
                        print(f"similar {k} and {k2}")

if __name__== "__main__":
  main()                
        

