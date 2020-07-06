import random
import shutil
import string
import time
import praw
import shlex, subprocess
from PIL import Image, ImageOps
import requests
from io import BytesIO
import numpy as np
from skimage import io
from google.cloud import vision
from google.cloud.vision import types
import io as io2
import os
from pypexels import PyPexels
import datetime

api_key = ''

def funct(filename=None, out=None, ang=str(90), sort="lightness", thresUp=None, thresLow=None):

    command = "python3 pixelSorter/pixelsort.py " + filename + " -s " + sort + " -u " + thresUp + " -t " + thresLow + " -o " + out + ".png" + " -a " + ang

    tradeLog(command)

    args = shlex.split(command)

    subprocess.run(args)


def calculate_brightness(image):

    greyscale_image = image.convert('L')
    histogram = greyscale_image.histogram()
    pixels = sum(histogram)
    brightness = scale = len(histogram)

    for index in range(0, scale):
        ratio = histogram[index] / pixels
        brightness += ratio * (-scale + index)

    return 1 if brightness == 255 else brightness / scale


def mse(img1, img2):
    squared_diff = (img1 - img2) ** 2
    summed = np.sum(squared_diff)
    num_pix = img1.shape[0] * img1.shape[1]
    err = summed / num_pix
    return err


def sort_the_image(filename="images/image.png", out="output/imageout"):

    image_different = False

    sortfunc = "lightness"

    retries = 0

    while image_different == False:

        tradeLog("Starting sort")

        brightness = calculate_brightness(Image.open(filename))

        tradeLog("Image brighness: ", brightness)

        # Threshold low amount
        low =  random.randint(0, 100)

        # Minimum MSE return for image to pass
        limit = 150

        if brightness < 0.6:
            low = random.randint(1, 60)

        if brightness < 0.5:
            low = random.randint(1, 50)

        if brightness < 0.4:
            low = random.randint(1, 40)

        if brightness < 0.3:
            low = random.randint(1, 30)

        if brightness < 0.1:
            low = random.randint(0, 10)
            limit = 60

        # Threshold high amount always low + 15 and < 100
        lowMax = low + 15

        if lowMax > 100:
            lowMax = 90

        up = random.randint(lowMax, 100)

        low = low / 100

        up = up / 100

        # Running script in seperate method
        funct(filename=filename, out=out, thresUp=str(up), thresLow=str(low), sort=sortfunc)

        # Input image
        imgA = io.imread(filename)

        # Output image
        imgB = io.imread(out + ".png")

        imgA = imgA[..., :3]
        imgB = imgB[..., :3]

        image_difference = mse(imgA, imgB)

        tradeLog("Difference: ", image_difference)

        tradeLog("Tries: ", retries)

        tradeLog("\n")

        if image_difference > limit:
            image_different = True

        retries = retries + 1

        if retries > 3:
            brightness = 0.25

        if retries > 5:
            brightness = 0.1

        if retries > 7:
            image_different = True

    if retries > 7:
        return "false"

    return out + ".png"

def image_urls(reddit, subreddit="nocontextpics"):

    pictureURLS = []

    subreddit = reddit.subreddit(subreddit)

    hot = subreddit.hot()

    for x in hot:
        if ((int(time.time()) - x.created_utc) / 60) < 1080:
            if x.score > 10:
                pictureURLS.append(x.url)

    return pictureURLS

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def get_the_image(url=""):

    response = requests.get(url)

    img = Image.open(BytesIO(response.content))

    size = (1080, 1080)

    img = ImageOps.fit(img, size)

    img.save("images/image.png")

def get_and_sort_image(url=""):

    sortedImage = "false"

    get_the_image(url=url)

    sortedImage = sort_the_image(filename="images/image.png", out="output/" + randomString())

    return sortedImage

def get_labels(imagePath="images/image.png"):

    tradeLog("Getting labels from Vision API")

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]\
        = ""

    client = vision.ImageAnnotatorClient()

    file_name = os.path.join(
        os.path.dirname(__file__),
        imagePath)

    with io2.open(file_name, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    response = client.label_detection(image=image)
    labels = response.label_annotations

    return labels

def make_comment(labelss=[]):

    amount = random.randint(5,25)

    randomHashtag1 = random.randint(0, amount)
    randomHashtag2 = random.randint(0, amount)
    randomHashtag4 = random.randint(0, amount)
    randomHashtag5 = random.randint(0, amount)
    randomHashtag6 = random.randint(0, amount)
    randomHashtag7 = random.randint(0, amount)
    randomHashtag8 = random.randint(0, amount)
    randomHashtag9 = random.randint(0, amount)

    comment = ""

    count = 0
    for label in labelss:
        if count < amount:
            if count == randomHashtag1:
                if "glitchart" not in comment:
                    comment = comment + " #glitchart"

            if count == randomHashtag2:
                if "#glitch" not in comment:
                    comment = comment + " #glitch"

            if count == randomHashtag4:
                if "#surrrealism" not in comment:
                    comment = comment + " #surrrealism"

            if count == randomHashtag5:
                if "#abstract" not in comment:
                    comment = comment + " #abstract"

            if count == randomHashtag6:
                if "#abstractart" not in comment:
                    comment = comment + " #abstractart"

            if count == randomHashtag7:
                if "#psycadelicart" not in comment:
                    comment = comment + " #psycadelicart"

            if count == randomHashtag8:
                if "#distorted" not in comment:
                    comment = comment + " #distorted"

            if count == randomHashtag9:
                if "#aesthetic" not in comment:
                    comment = comment + " #aesthetic"

            if count == 0:
                hashtag = "#"
            else:
                hashtag = " #"


            comment = comment + hashtag + str(label.description).replace(" ", "")
            count = count + 1

    tradeLog(comment)

    return comment

def post(imagefp="", caption=""):
    currentDirectory = os.getcwd()
    shutil.move(currentDirectory + "/" + imagefp, currentDirectory +
                "/instabot/examples/photos/media" + '/' + imagefp.split("/")[-1])
    os.chdir(currentDirectory + "/instabot/examples/photos")

    command = "python3 upload_photos.py -photo " + imagefp.split("/")[-1] + " -caption " + '"' + caption + '"'

    args = shlex.split(command)

    try:
        subprocess.run(args, timeout=240)
        os.chdir(currentDirectory)
    except Exception as e:
        os.chdir(currentDirectory)
        tradeLog("Upload process timeout: ", e)
        time.sleep(500)

def postv2(path="", caption=""):

    from InstagramAPI import InstagramAPI

    InstagramAPI = InstagramAPI("username", "password")
    InstagramAPI.login()  # login

    photo_path = path
    caption = caption

    image = Image.open(path)
    rgb_im = image.convert('RGB')
    rgb_im.save('images/topost.jpg')
    image = Image.open('images/topost.jpg')
    data = list(image.getdata())
    image_without_exif = Image.new(image.mode, image.size)
    image_without_exif.putdata(data)

    image_without_exif.save('images/topost.jpg')

    tradeLog("Uploading to instagram")
    InstagramAPI.uploadPhoto('images/topost.jpg', caption=caption)


def cleanImage(path):
    image = Image.open(path)
    rgb_im = image.convert('RGB')
    rgb_im.save('images/topost.jpg')
    image = Image.open('images/topost.jpg')
    data = list(image.getdata())
    image_without_exif = Image.new(image.mode, image.size)
    image_without_exif.putdata(data)
    newname = "images/" + randomString() + ".jpg"
    image_without_exif.save(newname)
    return newname

def searchPhotos(searchTerm = "", amountPerPage = 10, AmountOfPages = 5, AmountOfPagesToSkip= 5):

    theurls = []

    py_pexel = PyPexels(api_key=api_key)

    search_results = py_pexel.search(query=searchTerm, per_page=amountPerPage)

    cc = 0
    c2 = 0
    c3 = 0

    tradeLog("Searching for: ", searchTerm)

    while search_results.has_next and c2 < AmountOfPages:

        if c3 > AmountOfPagesToSkip:

            for photo in search_results.entries:

                if photo.photographer != "Pixabay":

                    theurls.append([photo.src.get("original"), photo.photographer])

                    cc = cc + 1

            c2 = c2 + 1

        search_results.get_next_page()

        c3 = c3 + 1


    return theurls



def getPhoto():

    keywords = ["Space", "Abstract", "Urban", "Landscape", "Nature", "Sky", "Clouds", "Desert", "Forest", "Mountain", "Neon", "Tech"]

    allurls = []

    for keyword in keywords:
        urls = searchPhotos(searchTerm=keyword, amountPerPage=100, AmountOfPages=1, AmountOfPagesToSkip=5)
        allurls.append(urls)

    xx = 0
    for x in allurls:
        for y in x:
            xx = xx + 1

    tradeLog("Total pics: ", xx)

    final = []

    while len(final) < 2:

        final = random.choice(allurls)

    final = random.choice(final)

    tradeLog("Final ", final)

    return final

def runMain():

    url_author = getPhoto()
    filename = get_and_sort_image(url=url_author[0])

    countfail = 0
    while filename == "false":
        if countfail < 3:
            url_author = getPhoto()
            tradeLog("Fail. Retrying")
            filename = get_and_sort_image(url=url_author[0])
            countfail = countfail + 1
        else:
            filename == ""

    if countfail > 3:
        tradeLog("TOO MANY FAILS RIP")
        return False

    else:

        #filename = get_and_sort_image(url="https://images.pexels.com/photos/39811/pexels-photo-39811.jpeg")

        labels = get_labels()
        comment = make_comment(labels)
        comment = comment + " Pic by: " + url_author[1]
        uniqueName = cleanImage(filename)
        post(imagefp=uniqueName, caption=comment)
        tradeLog("ALL SUCESS")

        return True

def tradeLog(msg, msg2=""):

    msg = str(msg)
    msg2 = str(msg2)

    print(msg, msg2)

    f2 = open("tradelog.txt", "a")

    f2.write(str(datetime.datetime.now()) + ", " + str(msg) + " " + str(msg2) + "\n")

    f2.close()

def logtime():

    f2 = open("timelog.txt", "a")

    f2.write(str(time.time()) + "\n")

    f2.close()

def checkTime():
    f = open('timelog.txt', 'r')
    lines = f.read().splitlines()
    last_line = lines[-1]
    time_passed = float(time.time()) - float(last_line)
    return time_passed

while True:

    try:
        print("Minutes since last run: (Limit 500 min)  ", checkTime()/60)
        if checkTime() > 30000:
            tradeLog("Starting run!!", time.time())

            run1 = runMain()

            if run1:
                logtime()
                tradeLog("WAITING UNTIL NEXT POST 9hrs", time.time())
                for x in range(0,10):
                    tradeLog("Zzz...", x)
                    time.sleep(3240)

        else:
            tradeLog("Retrying to post in 20 minutes. Checktime: " + str(checkTime()), time.time())
            time.sleep(1200)

    except Exception as e:
        tradeLog(e)
        tradeLog("Exception. Sleeping for 9hrs")

        for x in range(0, 10):
            tradeLog("Sleeping after exception ", x)
            time.sleep(3240)

