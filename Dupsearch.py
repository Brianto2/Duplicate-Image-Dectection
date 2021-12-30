# Program that detects for smaller duplicate images from a folder.
# O(n^2) runtime

import shutil
import os.path
import imagehash
from PIL import Image, UnidentifiedImageError
from tkinter import Tk
from tkinter.filedialog import askdirectory
import time


# Core driver of the program. Gets a directory from the user and processes the folder for duplicate images
# Accuracy: Needs to be in values of base 2.
#           Determines how accurate the duplicates need to be. Images with slight variations/versions maybe falsely
#           detected as dupes at low accuracy levels. Use 64 or 128. 256+ is overkill
def find_dupes(accuracy):
    start_time = time.time()
    imgtable = {}
    dupelist = []
    # UI stuff, get the file location
    Tk().withdraw()  # hides ui since we only need the open folder ui
    root = askdirectory()  # opens folder ui

    f = get_dirs(root)
    dupelist = process_list(f, imgtable, dupelist)

    print("--- %s seconds ---" % (time.time() - start_time))

    dupelist = recheck_d(accuracy, dupelist)
    print("---Total runtime %s seconds ---" % (time.time() - start_time))
    return dupelist


# Get a list of all files the directory and subdirectories and returns a list of files
def get_dirs(root):
    f = []
    print("Gathering list of files")
    for root, dirs, files in os.walk(root, topdown=False):
        for name in files:
            f.append(os.path.join(root, name))
        for name in dirs:
            f.append(os.path.join(root, name))
    return f


# "Quickly" process list for duplicates, saves time in recheck_d
# f: files
# imgtable: dictionary of images using the image hash as a key and a list of images as values
# dupelist: a list of tuples to compare in recheck_d
def process_list(f, imgtable, dupelist):
    print("Processing List, ", len(f), "items")
    counter = 0
    for f_img in f:
        if os.path.isfile(f_img):
            # Ignore gifs because resizing the images results in a still image. When this image is hashed it is a fp.
            if not f_img.endswith("gif"):
                try:
                    img = Image.open(f_img)
                    # get the hash of the image
                    hash_of_img = str(imagehash.average_hash(img, 64))
                    # if key already exists then update the list at the given key
                    if imgtable.get(hash_of_img):
                        olist = imgtable.get(hash_of_img)
                        # create tuples of the new file with the old files to check duplicates for
                        for x in olist:
                            dupelist.append((x, f_img))
                        # update the list in image table
                        olist.append(f_img)
                        imgtable.update({hash_of_img: olist})
                    else:
                        imgtable.update({hash_of_img: [f_img]})

                # if the file is not a valid pil image file skip it
                except UnidentifiedImageError:
                    print("Invalid file extension :", f_img)
                    pass
        counter += 1
    print("Processed: ", counter)
    return dupelist


# Recheck using D-hash, more accurate than average hash while faster than phash at large size values
# dupelist: list of duplicates to recheck
def recheck_d(img_size, dupelist):
    # process dupes again with better accuracy
    print("Rechecking Duplicates: ", len(dupelist))
    newtime = time.time()
    for x in list(dupelist):
        hash1 = imagehash.dhash(Image.open(x[0]), img_size)
        hash2 = imagehash.dhash(Image.open(x[1]), img_size)

        if hash1 != hash2:
            dupelist.remove(x)
        else:
            print(x[1], "      ", x[0])

    print("Dupes found: ", len(dupelist))
    print("---Run time: %s seconds ---" % (time.time() - newtime))
    return dupelist


# Move pairs to different folder
# dupelist: list of duplicates to move
def move(dupelist):
    if len(dupelist) != 0:
        # get the output folder
        Tk().withdraw()
        o = askdirectory()
        for item in dupelist:
            try:
                shutil.move(item[0], o)
                shutil.move(item[1], o)

            except Exception as e:
                print(e)
    else:
        print("No dupes")
