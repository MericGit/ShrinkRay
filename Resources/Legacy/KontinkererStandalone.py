import os
import subprocess
import time
import datetime
from shutil import copyfile

#Initialize Vars. Do not modify unless you are using a custom FFMPEG or xCON build
current = 0
count = 0
xCon = os.path.dirname(os.path.realpath(__file__)) + "/Resources/conNCW04.exe"
ffmpeg = os.path.dirname(os.path.realpath(__file__)) + "/Resources/ffmpegReduced.exe"

#Set this to the folder containing a folder that contains your samples. No ncw should be directly in this dir, only a folder containing them.
#Designed this way to easily accomodate direct ncx unpacking into this dir. 
rootdir = os.path.dirname(os.path.realpath(__file__)) + "/Resources/Default"
micTarget = ["!"]
#micTarget = ["ab,","close1","close2","close","surround","AB","CLOSE1","CLOSE2","CLOSE","SRND","SUR","SURROUND"]   #Mic positions you want to delete. Case sensitive, type exactly as is in the filename.
whitelist = ["!null"]  #Samples containing these words are ignored and not processed.
doShrink = False


def scan():
    global count
    count = 0
    print("Beginning Stage A: Pre-Startup")
    print("Scanning For samples...")
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            if file.endswith("ncw"):
                count += 1
            else:
                print("NON ncw file: " + os.path.join(subdir,file) + " found")
                #os.remove(os.path.join(subdir,file))
    print(str(count) + " Samples found.")


def osWalk():
    global count
    global current
    print("Beginning Stage B: Mic Deletion and File Shrinking")
    print("Targeting Samples...")
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            try:
                if file.endswith("ncw"):
                    current += 1
                    if micDelete(subdir, file) is False:
                        #print('(' + str(current) + ' / ' + str(count) + ') ', end='')
                        if doShrink is True:
                            print('(' + str(current) + ' / ' + str(count) + ')',end='')
                            shrink(subdir,file)
                else:
                    print("NON ncw file located in directory - Ignoring file: " + os.path.join(subdir,file))
            except KeyboardInterrupt:
                print('\nPausing...  (Hit ENTER to continue, type quit to exit.) BTW this is kind of broken. You will have a few non-converted or wav files remaining.')
                try:
                    response = input()
                    if response == 'quit':
                        return
                    print('Resuming...')
                except KeyboardInterrupt:
                    print ('Resuming...')
                    continue
def shrink(subdir,file):
        subprocess.call([xCon,os.path.join(subdir,file)])
        print("\033[A\033[A")
        subprocess.call([ffmpeg, '-hide_banner', '-loglevel', 'error','-y','-i', os.path.join(subdir, file.replace('ncw','wav',1)),'-acodec', 'pcm_s16le', '-af', 'aresample=osf=s16:dither_method=rectangular', '-nostdin',os.path.join(subdir, "C" + file.replace('ncw','wav',1))])
        os.remove(os.path.join(subdir,file.replace('ncw','wav',1)))
        os.remove(os.path.join(subdir,file))
        os.rename(os.path.join(subdir, "C" + file.replace('ncw','wav',1)),os.path.join(subdir, file.replace('ncw','wav',1)))
        subprocess.call([xCon,os.path.join(subdir,file.replace('ncw','wav',1))])
        print("\033[A\033[A")
        os.remove(os.path.join(subdir,file.replace('ncw','wav',1)))
def micDelete(subdir, file):
    global micTarget
    if not any(ignore in file for ignore in whitelist) and any(mic in file for mic in micTarget):
        copyfile(os.path.dirname(os.path.realpath(__file__)) + "/Resources/micReplace.ncw", os.path.join(subdir,file))
        return True
    else:
        return False


def run():
    start = time.time()
    print("Script start: " + str(start))
    scan()
    osWalk()
    end = time.time()
    print("Shrink finished in: " + str(datetime.timedelta(seconds=int(end - start))))





