#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt
import cv2
from Dataset import mask2categorical, parse_labelfile
from sys import argv, stderr
from datetime import datetime

USAGE = f"USAGE [OPTIONS ...] [PNG_IMG] [TXT_FILE]\n"
USAGE += "Count the segmented objects of a predicted or true mask image\n\n"
USAGE += "OPTIONS:\n\t"
USAGE += "-v --verbose: show the boxes around the pixels in the image\n\t"
USAGE += "--stats: show the width and height in milimeters of the object\n\t"

def filter_boxes(stats):
    boxes = []
    for i,stat in enumerate(stats):
        if stat[-1] > 1200 and i!=0:
            boxes.append(stat[:-1])
    return np.array(boxes)

def count_seeds(img, boxes, labels):
    Img = img.copy()
    if Img.dtype != "uint8":
        Img = (255 * Img).astype("uint8")

    count = [0]*(len(labels) - 1)
    for i, box in enumerate(boxes):
        y, x, h, w = box
        x1, y1 = x, y
        x2, y2 = x + w, y + h
        img_box = Img[x1:x2, y1:y2]
        S = [(img_box == labels[key]).sum() 
                for key in labels]
        j = np.argmax(S[1:])
        count[j] += 1
    label_keys = list(labels.keys())[1:]
    return {key: count[i] for i, key in enumerate(label_keys)}

def draw_boxes(img, boxes, XY=False):
    X = (img.copy()*255).astype("uint8")
    if XY:
        file = open("weights/config.csv")
        XY_dims = file.readlines()[1].strip("\n").split(",")
        XY_dims = np.array(XY_dims).astype("float32")

    for i, box in enumerate(boxes):
        pt1 = box[:2]
        pt2 = pt1 + box[2:4] 
        pt1 = tuple(pt1.tolist())
        pt2 = tuple(pt2.tolist())
        COLOR = tuple([255, 255, 255])
        X = cv2.rectangle(X, pt1, pt2, COLOR, 2)

        if XY:
            width, height = box[2:]*XY_dims
            orgw = pt1[0] + int(box[2]//2.5), pt1[1]
            orgh = pt1[0], pt1[1] + int(box[3]//1.5)
            FontScale = 1
            X = cv2.putText(X, f"{width:.2f}", 
                            orgw, cv2.FONT_HERSHEY_SIMPLEX,
                            FontScale, (255, 255, 255),
                            thickness=2)
            X = cv2.putText(X, f"{height:.2f}", 
                            orgh, cv2.FONT_HERSHEY_SIMPLEX,
                            FontScale, (255, 255, 255),
                            thickness=2)
    return X

if __name__ == "__main__":
    args = [arg for arg in argv[1:] if not arg.startswith("-")]
    opts = [opt for opt in argv[1:] if opt.startswith("-")]

    if len(args) == 2:
        IMG_PATH = tuple(arg for arg in args if arg[-3:] == "png")[0]
        LABEL_PATH = tuple(arg for arg in args if arg[-3:] == "txt")[0]
        LABELS = parse_labelfile(LABEL_PATH)

        img = plt.imread(IMG_PATH)
        img_int = (img*255).astype("uint8")
        mask = mask2categorical(img, LABELS).numpy()
        count, n_img, stats, centroids = cv2.connectedComponentsWithStats(mask)
        boxes = filter_boxes(stats)

        lcount = count_seeds(img_int, boxes, LABELS)

        print(f"germinated:\t {lcount['germinated']}")
        print(f"no_germinated:\t {lcount['no_germinated']}")

        if "-v" in opts or "--verbose" in opts:
            if "--stats" in opts:
                dimg = draw_boxes(img, boxes, XY=True)
            else:
                dimg = draw_boxes(img, boxes)

            fig, ax = plt.subplots(1, 2)
            ax[0].imshow(img)
            ax[1].imshow(dimg)
            ax[0].axis("off")
            ax[1].axis("off")

            total = lcount["germinated"] + lcount["no_germinated"]
            today = datetime.now()
            stitle = f"{today.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            stitle += f"Total semillas detectadas: {total}\n"
            title = f"Total semillas germinadas: {lcount['germinated']}   "
            title += f"Total semillas no germinadas: {lcount['no_germinated']}"

            fig.suptitle(stitle)
            fig.text(.5, .05, title, ha="center", fontsize="large")
            plt.show()
    else:
        print(USAGE, file=stderr)

