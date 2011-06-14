# Archives a feed. Pulls from the source, saves appropriate resources.
# Not terribly complete, but perhaps sufficient.
#
# TODO: Reduce dependencies? This uses everything under the
# sun. Batteries REQUIRED!
#
from elementtree.ElementTree import ElementTree, tostring
import xml.dom.minidom
import feedwriter
import feedparser
import rsswriter
import urllib
import os
import os.path
import sys
import ConfigParser
import time
import httplib2
import logging



def progress(blocks, size, fileSize):
    bytes = blocks * size
    percent = (float(bytes) / float(fileSize))
    sys.stdout.write("[%-40s] %d%% (%d/%d)\r" % ('='*int(40*percent), (percent * 100.0), bytes, fileSize))

def downloadLocal(url):
    """Download the url to a local file and return the name of the local
    file.

    Ideally this would be cache-aware. httlib2 is cache-aware, but it
    forces me to load the entire response into memory. If we got
    streaming support in httplib2 then we could use it.
    """
    localDir = os.path.join(baseDir, "local")
    if not os.path.exists(localDir): os.makedirs(localDir)

    local = os.path.join(localDir, httplib2.safename(url))
    if not os.path.exists(local):
        try:
            print "Getting", url, "as", local
            logging.info("Getting %s as %s", url, local)
            urllib.urlretrieve(url, local, progress)
        except:
            if (os.path.exists(local)): os.unlink(local)
            raise

    return local

def convertUrlIf(base, url):
    """Convert the url to a local one, if it's something we can download."""
    if url == None: return url
    if not url[:4] == "http": return url
    
    local = downloadLocal(url)
    return base + urllib.pathname2url(local)

def convertLocal(feed, base):
    """Download all the stuff in the feed that might refer to
    something remote.

    If we were very, very clever, we would download all sorts of
    things, and spider the whole content. But we aren't, yet.
    """
    if feed.feed.has_key("image"):
        feed.feed.image.href = convertUrlIf(base, feed.feed.image.get("href"))
        feed.feed.image.link = convertUrlIf(base, feed.feed.image.get("link"))

    for entry in feed.entries:
        for enclosure in entry.enclosures:
            enclosure.href = convertUrlIf(base, enclosure.href)
            
        for link in entry.links:
            if link.rel != "enclosure": continue
            link.href = convertUrlIf(base, link.href)


def archiveFeed(config):
    global baseDir, feedName, rssName

    url = config.get("feed","url")
    publish = config.get("feed", "publish")
        
    # Download the feed and also its enclosures.
    #
    print "Fetching", url
    logging.info("Fetching %s", url)
    fr = feedparser.parse(url)
    convertLocal(fr, publish)

    # Merge the remote feed into the local feed
    #
    if os.path.exists(feedName):
        fl = feedparser.parse(feedName)
        em = dict([(e.id, True) for e in fl.entries])
        for entry in fr.entries:
            if not em.has_key(entry.id):
                entry.source = fr.feed
                fl.entries.append(entry)
    else:
        fl = feedparser.FeedParserDict({
            "feed" : feedparser.FeedParserDict({
                "id" : config.get("feed","id"),
                "link" : publish + "feed.rss",
                "image" : fr.feed.get("image"),
                "links" : [feedparser.FeedParserDict({
                    "rel" : "self",
                    "type" : "application/atom+xml",
                    "href" : publish + "feed.xml"
                })],
                "title_detail" : feedparser.FeedParserDict({
                    "type" : "text",
                    "value" : config.get("feed", "title")
                }),
                "subtitle_detail" : fr.feed.get("subtitle_detail")
            }),
            "entries" : fr.entries
        })
        for entry in fr.entries:
            entry.source = fr.feed

    # Back up the local feed.
    #
    backupRoot = time.strftime("%Y%m%d.%H%M%S.feed")

    # Write out the local feed.
    #
    atomRoot = feedwriter.GetFeedElement(fl)
    if os.path.exists(feedName):
        os.renames(feedName,os.path.join(baseDir,"backup",backupRoot+".xml"))
    ElementTree(atomRoot).write(feedName)

    rssRoot = rsswriter.GetFeedElement(fl)
    if os.path.exists(rssName):
        os.renames(rssName,os.path.join(baseDir,"backup",backupRoot+".rss"))
    ElementTree(rssRoot).write(rssName)

if len(sys.argv) > 1:
    configFile = sys.argv[1]
else:
    configFile = os.path.join(".", "feed.ini")

baseDir = os.path.dirname(os.path.abspath(configFile))
feedName = os.path.join(baseDir, "feed.xml")
rssName = os.path.join(baseDir, "feed.rss")

print "Using config in", configFile
print "Base directory", baseDir
    
config = ConfigParser.RawConfigParser()
config.read(configFile)
archiveFeed(config)
print "Done"

