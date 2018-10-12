import os
import pandas as pd
from bs4 import BeautifulSoup
import voc_utils
from more_itertools import unique_everseen
from shutil import copyfile

root_dir = '/hdd/Downloads/VOCdevkit/VOC2007/'
img_dir = os.path.join(root_dir, 'JPEGImages')
ann_dir = os.path.join(root_dir, 'Annotations')
set_dir = os.path.join(root_dir, 'ImageSets', 'Main')
groundtruth_dir = '/hdd/Object-Detection-Metrics/groundtruths/'#/hdd/pascal-voc-python/groundtruth/'

# list image sets
all_files = os.listdir(set_dir)
image_sets = sorted(list(set([filename.replace('.txt', '').strip().split('_')[0] for filename in all_files])))
print image_sets

# category name is from above, dataset is either "train" or
# "val" or "train_val"
def imgs_from_category(cat_name, dataset):
    filename = os.path.join(set_dir, cat_name + "_" + dataset + ".txt")
    df = pd.read_csv(
        filename,
        delim_whitespace=True,
        dtype={'filename':object, 'true':int},
        header=None,
        names=['filename', 'true'])
    return df

def imgs_from_category_as_list(cat_name, dataset):
    df = imgs_from_category(cat_name, dataset)
    df = df[df['true'] != 0]  # 0 means difficult and not included for evaluation
    return df['filename'].values

def annotation_file_from_img(img_name):
    return os.path.join(ann_dir, img_name) + '.xml'


# annotation operations
def load_annotation(img_filename):
    xml = ""
    with open(annotation_file_from_img(img_filename)) as f:
        xml = f.readlines()
    xml = ''.join([line.strip('\t') for line in xml])
    return BeautifulSoup(xml)

def get_all_obj_and_box(objname, img_set):
    img_list = imgs_from_category_as_list(objname, img_set)

    for img in img_list:
        annotation = load_annotation(img)


# image operations
def load_img(img_filename):
    return io.load_image(os.path.join(img_dir, img_filename + '.jpg'))

test_img_list = imgs_from_category_as_list('car', 'test')
print test_img_list
print test_img_list.size

a = load_annotation(str(test_img_list[0]))

for item in test_img_list:
    anno = load_annotation(item)
    objs = anno.findAll('object')
    fname = anno.findChild('filename').contents[0]
    copyfile(os.path.join(img_dir, fname),
            os.path.join('/hdd/YOLO/data/VOC2007/JPEGImages/car/', fname))
    f = open(os.path.join(groundtruth_dir, item) + '.txt', 'w+')
    for obj in objs:
        obj_names = obj.findChildren('name')
        for name_tag in obj_names:
            if str(name_tag.contents[0]) == 'car':
                bbox = obj.findChildren('bndbox')[0]
                xmin = int(bbox.findChildren('xmin')[0].contents[0])
                ymin = int(bbox.findChildren('ymin')[0].contents[0])
                xmax = int(bbox.findChildren('xmax')[0].contents[0])
                ymax = int(bbox.findChildren('ymax')[0].contents[0])
                print("car %d %d %d %d" % (xmin, ymin, xmax, ymax))
                f.write("car %d %d %d %d\n" % (xmin, ymin, xmax, ymax))
