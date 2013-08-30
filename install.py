import shutil
from subprocess import call
import urllib
import urllib2
import zipfile
import time
from progress import ProgressBar


__author__ = 'altryne'

import os, alfred

(action, query) = alfred.args() # proper decoding and unescaping of command line arguments

DOWNLOADS_FOLDER = os.path.join(os.path.expanduser('~'), 'Downloads')
APP_FOLDER = os.path.join(os.path.expanduser('~'), 'Applications')

def get_raw_file(request_data=None):
    request_url = query
    request = urllib2.Request(request_url, request_data, {})
    response = urllib2.urlopen(request)
    return response.read().splitlines()


info = get_raw_file()[1:][:-1]
obj = {}
for line in info:
    key, val = line.strip().partition(' ')[::2]
    obj[key] = val

print obj


def extract_files(dirname):
    for root, dirs, files in os.walk(dirname, True, None):
        remove = [".background", ".Trashes", ".DS_Store", "Applications"]

        for idir in dirs:
            if dir in remove:
                continue
            dname, ext = os.path.splitext(idir)
            if (ext == '.app'):
                path = os.path.join(root, idir)
                try:
                    bar.update(100, message="Copying to ~/Applications folder...")
                    shutil.copytree(path, os.path.join(APP_FOLDER, idir), symlinks=True)
                    bar.update(100, message="Done! App was installed")
                except Exception as e:
                    print e
                    bar.update(100, message="Err : %s" % e)
                return

        for lfile in files:
            if lfile in remove:
                continue
            fname, ext = os.path.splitext(lfile)
            if not fname.startswith('.') and ext == '.dmg':
                # print 'DMG FOUND!! install dmg!'
                mount_and_install(os.path.join('tmp', lfile))
                break
            elif ext == '.pkg':
                # print 'PKG file found. OMG OGM'
                break
        else:
            continue


def mount_and_install(filename):
    if not os.path.exists('tmp'):
        os.makedirs('tmp')
    # print 'trying to mount %s' % filename
    try:
        shell_command = 'hdiutil attach -mountpoint "%s" %s' % ('tmp/my-temp-mount', os.path.abspath(filename))
        print shell_command
        call(shell_command, shell=True)
        try:
            extract_files('tmp/my-temp-mount')
        finally:
            call('hdiutil detach "tmp/my-temp-mount"', shell=True)
    except Exception as e:
        print 'err!! : %s' % e
    pass


def unzip_and_install(filename):
    zfile = zipfile.ZipFile(filename)
    #change dir to downloads folder

    #create a temporary dir
    if not os.path.exists('tmp'):
        os.makedirs('tmp')

    zfile.extractall('tmp')

    extract_files('tmp')

    #cleaning up
    shutil.rmtree('tmp')


try:
    url = obj["url"][1:][:-1]
    name = obj["url"][1:][:-1].split('/')[-1]
    filename = os.path.join(DOWNLOADS_FOLDER, name)
    name, ext = os.path.splitext(filename)

    bar = ProgressBar(title="Downloading Started : Downloading %s V. %s " % (name, obj["version"]))

    if(ext not in [".app",".zip",".pkg",".dmg"]):
        bar.update(0, message="Can't handle files of type %s" % ext)
        time.sleep(2)
        raise

    os.chdir(DOWNLOADS_FOLDER)

    def prg(count, blockSize, totalSize):

        percent = int(count * blockSize * 100 / totalSize)
        bar.update(percent,message="(%s%%) Downloading %s " % (percent,url))



    urllib.urlretrieve(url, filename, reporthook=prg)
    print "\n"

    #this is needed so lion won't collate notifications
    bar.update(100, message="Download finished, please wait while I unpack and install")


    # try to unpack



    if (ext == '.zip'):
        print "zip file found, unzipping"
        bar.update(100, message="Unzipping...")
        unzip_and_install(filename)
    elif (ext == '.dmg'):
        print "dmg file found, mounting"
        bar.update(100, message="Mounting....")
        mount_and_install(filename)
    else:
        bar.update(100, message="Can't handle files of type %s" % ext)
        print "can't handle this file"

    # cleanup remove downloaded file

    os.remove(filename)
    time.sleep(3)
    bar.finish()

except Exception as e:
    print 'oops : %s' % e



