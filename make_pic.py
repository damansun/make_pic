from PIL import Image,ImageDraw,ImageFont
import os
import random
from optparse import OptionParser
# [Coulson]: from tqdm import tqdm
import json
from imutils import paths
from datetime import datetime

__author__ = "Xuefeng Sun"
__version__ = "v0.2"

AVALIABLE_PATH = ".history/avaliable.json"
USED_PATH = ".history/used.json"

config = {}

def load_file(file_path):
    try:
        with open(file_path) as json_file:
            data = json.load(json_file)
            return data
    except:
        # [Coulson]: print("%s is not found"%file_path)
        raise

def save_file(file_path, data):
    with open(file_path, 'w') as json_file:
        json_file.write(json.dumps(data))

## Parse command line options
#
# Using standard Python module optparse to parse command line option of this tool.
#
#   @retval Opt   A optparse.Values object containing the parsed options
#   @retval Args  Target of build command
#
def option_parser():
    Parser = OptionParser(description='''Draw the text on give image.''',
                        version='0.2', usage='''make_pic.py [options] <image path>''')
    Parser.add_option("-u", "--update", dest="update", action="store_true", help="update image database")
    Parser.add_option("-d", "--reset-to-default", dest="default", action="store_true", help="restart database to default")
    Parser.add_option("-n", "--number", dest="number", action="store", help="Input the number of images")

    (Opt, Args) = Parser.parse_args()
    return (Opt, Args)


def image_resize(img, size=(1500, 1100)):
    """resize image
    """
    try:
        if img.mode not in ('L', 'RGB'):
            img = img.convert('RGB')
        img = img.resize(size)
    except:
        pass
    return img

def adaptive_property(img_size, text_length, font_size, random_y = False):
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
        if random_y:
            txt_property["y"] = random.randint(figure["left_top"][1], figure["right_bottom"][1] - font_size[1] * 2 * txt_property["lines"])
        else:
            txt_property["y"] = figure["left_top"][1]
    except:
        raise 

    return txt_property

def write_text(img, text, img_size = [0,0], start_point=[0,0], random=False):
    font_size = config["font_size"]
    for i in range(4):
        try:
            txt_pro = adaptive_property(img_size, len(text), font_size)
            break
        except:
            print("Try to scaling the font size...")
            font_size = [int(s * 0.7) for s in font_size]

    if i > 2:
        print("Too many words, stop to draw")
        raise RuntimeError

    myfont = ImageFont.truetype(config["ttf"],size=font_size[0])
    draw = ImageDraw.Draw(img)

    #insert \n for text
    text_list = list(text)
    text = []
    index = 1
    for t in text_list:
        if t != "\n":
            if index % txt_pro["words_per_line"] == 0:
                text.append("\n")
            index += 1
        else:
            index = 1
        text.append(t)

    text = ''.join(text)

    if random:
        color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
    else:
        color = config["color"]
    draw.multiline_text((start_point[0] + txt_pro["x"], start_point[1] + txt_pro["y"]), \
        text, tuple(color), font=myfont)
    return img

def image_merge(front_img, text, background_img=None):

    if background_img:
        new_img = image_resize(background_img, config["output_size"])
        pic_left_top = [config["pic_blank_edge"]["left"], config["pic_blank_edge"]["top"]]
        pic_target_size = [new_img.size[0] - config["pic_blank_edge"]["left"] - config["pic_blank_edge"]["right"],
                            new_img.size[1] - config["pic_blank_edge"]["top"] - config["pic_blank_edge"]["bottom"]]

        front_img = image_resize(front_img, pic_target_size)
    else:
        f_img_size = front_img.size
        x = f_img_size[0] + config["pic_blank_edge"]["left"] + config["pic_blank_edge"]["right"]
        y = f_img_size[1] + config["pic_blank_edge"]["top"] + config["pic_blank_edge"]["bottom"]
        new_img = Image.new('RGB', (x,y), (255,255,255))
        pic_left_top = [config["pic_blank_edge"]["left"], config["pic_blank_edge"]["top"]]

    new_img.paste(front_img, pic_left_top)

    txt_left_top = [config["txt_blank_edge"]["left"], new_img.size[1] - config["pic_blank_edge"]["bottom"]]
    txt_target_size = [new_img.size[0] - config["txt_blank_edge"]["left"] - config["txt_blank_edge"]["right"], config["pic_blank_edge"]["bottom"]]
    img = write_text(new_img, text, img_size=txt_target_size, start_point=txt_left_top)

    #drawing corner-mark
    myfont = ImageFont.truetype(config["ttf"],size=config["corner_mark_size"][0])
    draw = ImageDraw.Draw(img)
    draw.text([new_img.size[0] - (config["spacing"]["right"] + 1) * config["font_size"][0], 
        new_img.size[1] - (config["spacing"]["bottom"] + 1) * config["font_size"][0]], 
        config["corner_mark"], tuple(config["corner_mark_color"]), font=myfont)

    return new_img

def bulid_image_list(path):
    record = {
        "last_dir":path,
        "images_paths":None,
        "text":None
    }
    print("Generating image database ...")
    record["images_paths"] = list(paths.list_images(path))
    with open(config["text"], 'r', encoding="utf-8") as fin:
        text = fin.read()
    record["text"] = text.split("\n\n")
    try:
        used = load_file(USED_PATH)
        for key, data in used.items():
            data_type = key.split("_")[-1]
            for d in data:
                if data_type == "image":
                    record["images_paths"].remove(d)
                elif data_type == "text":
                    record["text"].remove(d)
                else:
                    print("unknown type")
    except:
        pass
    save_file(AVALIABLE_PATH, record)
    print("Completed, please run again!!!")

def generate_image(img_list, text, output_name):
    for i, img in enumerate(img_list):
        front_img = Image.open(img, mode="r")
        try:
            bg_img = Image.open(".config/default_bg.png", mode="r")
            merged_img = image_merge(front_img, text[i], bg_img)
        except:
            merged_img = image_merge(front_img, text[i])

        try:
            os.mkdir(output_name)
        except:
            pass
        filename_no_ext, ext = img.split(os.path.sep)[-1].split(os.path.extsep)
        filename = os.path.join(output_name, filename_no_ext + str(i) + "." + ext )
        merged_img.save(filename, quality=100)
        try:
            front_img.close()
            bg_img.close()
        except:
            pass

def main(image_path, image_count = 0):
    '''
    with open("text.txt", 'r', encoding="utf-8") as fin:
        text = fin.read()
    front_img = Image.open("images/1.jpg", mode="r")
    try:
        bg_img = Image.open(".config/default_bg.png", mode="r")
        img = image_merge(front_img, text, bg_img)
    except:
        img = image_merge(front_img, text)
    img.save("output/test.jpg", quality=100)
    '''
    try: 
        record = load_file(AVALIABLE_PATH)
    except:
        print("Initializing image database")
        bulid_image_list(image_path)
        return

    if not record["last_dir"] == image_path:
        print("Your input folder is not same with before, please add -u to update your image database")
        return
    else:
        min_len = min(len(record["images_paths"]), len(record["text"]))
        if min_len == 0:
            print("Out of resource!!!")
            return
        #Align text and image length
        record["images_paths"] = record["images_paths"][:min_len]
        record["text"] = record["text"][:min_len]
        images_list = record["images_paths"][:image_count]
        text_list = record["text"][:image_count]
        record["images_paths"] = record["images_paths"][image_count:]
        record["text"] = record["text"][image_count:]
        save_file(AVALIABLE_PATH, record)
        try:
            used = load_file(USED_PATH)
        except:
            used = {}
        date = datetime.now().strftime("%Y-%m-%d")
        strike = 0
        for n in used.keys():
            if date in n:
                strike = int(n.split("-")[-2])
        strike += 1
        folder_name = date + '-' + str(strike) + '-' + str(image_count)
        generate_image(images_list, text_list, config["output_path"] + folder_name)
        used[folder_name + "_image"] = images_list
        used[folder_name + "_text"] = text_list
        save_file(USED_PATH, used)
        return

if __name__ == "__main__":
    (option, args) = option_parser()

    if len(args) < 1 and not option.default:
        print("invalid parameters")
        exit()
    config = load_file(".config/Default-settings.json")
    if option.update:
        bulid_image_list(args[0])
        exit()
    if option.default:
        used = {}
        record = {"last_dir":None}
        save_file(AVALIABLE_PATH, record)
        save_file(USED_PATH, used)
        exit()
    if option.number:
        main(args[0], int(option.number))
    else:
        main(args[0], 100)

