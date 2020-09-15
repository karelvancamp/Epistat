import glob
import fitz
import re
from PIL import Image, ImageEnhance
import numpy as np
import os


def extract_images(from_, to_):
    for x in glob.glob(from_):
        doc = fitz.open(x)
        name = re.findall('\d{8}',x)[0]
        for i in range(len(doc)):
            for img in doc.getPageImageList(i):
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                prefix = to_
                if pix.n < 5:       # this is GRAY or RGB
                    pix.writePNG(f"{prefix}{name} p{i}-{xref}.png")
                else:               # CMYK: convert to RGB first
                    pix1 = fitz.Pixmap(fitz.csRGB, pix)
                    pix1.writePNG(f"{prefix}{name} p{i}-{xref}.png")
                    pix1 = None


def strip_colors(file,
                 save_to_subpath='black',
                 cutoff=200,
                 cutoff_grey=100,
                 saturation_multiplier=2):

    im = Image.open(file)
    im = im.convert('RGBA')

    converter = ImageEnhance.Color(im)
    im_saturation = converter.enhance(saturation_multiplier)
    data = np.array(im_saturation)

    white = (0, 0, 0)
    black = (255, 255, 255)
    red, green, blue, alpha = data.T
    min_ = np.minimum.reduce([red, green, blue])
    max_ = np.maximum.reduce([red, green, blue])
    areas = (red < cutoff) & (blue < cutoff) & (green < cutoff) & ((max_ - min_) < cutoff_grey)
    data[..., :-1][areas.T] = white
    data[..., :-1][~areas.T] = black

    img = Image.fromarray(data.astype('uint8'))

    path = os.path.dirname(file)
    file_ = os.path.basename(file)
    img.save(os.path.join(path, save_to_subpath, file_))


def strip_colors_folder(file_pattern, **args):
    for file in glob.glob(file_pattern):
        strip_colors(file, **args)

daily_from = r"C:\Users\karel\PycharmProjects\demo\data\epistat_daily\*202008*.pdf"
daily_to = r"C:\Users\karel\PycharmProjects\demo\derived data\epistat\daily all images\\"
daily_black = daily_to+'*'

extract_images(daily_from, daily_to)
strip_colors_folder(daily_black)

weekly_from = r"C:\Users\karel\PycharmProjects\demo\data\epistat weekly\*2020*.pdf"
weekly_to = r"C:\Users\karel\PycharmProjects\demo\derived data\epistat\weekly all images\\"
weekly_black = weekly_to + '*'

# extract_images(weekly_from, weekly_to)
# strip_colors_folder(weekly_black)