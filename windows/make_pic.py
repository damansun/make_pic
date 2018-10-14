from PIL import Image,ImageDraw,ImageFont
import os
import random
from tqdm import tqdm

__author__ = "Xuefeng Sun"
__version__ = "v0.3"

config = {
    "output_path":"output",
    "input_path":"images",
    "size":[25,25],
    "ttf":"fonts/STXihei.ttf",
    "text":"text.txt",
    "spacing": {"top":3, "bottom":1, "left":5, "right":1}
}

def adaptive_property(img_size, text_length, font_size = config["size"]):
    txt_property = {}
    txt_pixs = text_length * font_size[0]
    #figure points for drawing the text.
    figure = {"left_top":[config["spacing"]["left"] * font_size[0], 
                        config["spacing"]["top"] * font_size[1]],
            "right_bottom":[img_size[0] - config["spacing"]["right"] * font_size[0],
                        img_size[1] - config["spacing"]["bottom"] * font_size[1]],
             }

    figure_size = [img_size[0] - (config["spacing"]["right"] + config["spacing"]["left"]) * font_size[0],
                    img_size[1] - (config["spacing"]["top"] + config["spacing"]["bottom"]) * font_size[1]]

    txt_property["words_per_line"] = figure_size[0] // font_size[0]

    if figure_size[0] > txt_pixs:
        txt_property["lines"] = 1
    else:
        txt_property["lines"] = txt_pixs // figure_size[0] + 1
    try:
        txt_property["x"] = figure["left_top"][0]
        txt_property["y"] = random.randint(figure["left_top"][1], figure["right_bottom"][1] - font_size[1] * 2 * txt_property["lines"])
    except:
        raise 

    return txt_property

def write_text(img, text):
    font_size = config["size"]
    for i in range(4):
        try:
            txt_pro = adaptive_property(img.size, len(text), font_size)
            break
        except:
            print("Try to scaling the font size...")
            font_size = [int(s * 0.7) for s in font_size]

    if i > 2:
        print("Too many words, stop to draw")
        raise RuntimeError

    myfont = ImageFont.truetype(config["ttf"],size=font_size[0])
    draw = ImageDraw.Draw(img)
    lines = txt_pro["lines"]
    color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
    for line in range(lines):
        draw.multiline_text((txt_pro["x"], txt_pro["y"] + font_size[1] * 2 * line), \
            text[txt_pro["words_per_line"] * line:txt_pro["words_per_line"] * (line + 1)], color, font=myfont)
    return img

def main():
    image_paths = os.listdir(os.path.join(config["input_path"]))
    with open(config["text"], 'r', encoding="utf-8") as fin:
        text_lines = fin.readlines()
    pbar = tqdm(total=len(text_lines) * len(image_paths))
    for i, line in enumerate(text_lines):
        for image in image_paths:
            try:
                org_img = Image.open(os.path.join(config["input_path"], image))
            except:
                print("{} is not avaliable".format(image))
                continue
            img = write_text(org_img, line)
            try:
                os.mkdir(config["output_path"])
            except:
                pass
            filename_no_ext, ext = image.split(os.path.sep)[-1].split(os.path.extsep)
            filename = os.path.join(config["output_path"], filename_no_ext + str(i) + "." + ext )
            img.save(filename, quality=100)
            org_img.close()
            pbar.update(n=1)

if __name__ == "__main__":
    main()
