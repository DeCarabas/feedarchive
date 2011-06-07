# Archives a feed. Pulls from the source, saves appropriate resources.
# Not terribly complete, but perhaps sufficient.
# TODO: Mirror everything that could be local, local.
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

# Download the feed and also its enclosures.
#
def progress(blocks, size, fileSize):
    bytes = blocks * size
    percent = (float(bytes) / float(fileSize))
    sys.stdout.write("[%-40s] %d%% (%d/%d)\r" % ('='*int(40*percent), (percent * 100.0), bytes, fileSize))

def archiveFeed(config):
    url = config.get("feed","url")
    publish = config.get("feed", "publish")
    print "Fetching", url
    
    fr = feedparser.parse(url)
    for entry in fr.entries:
        for link in entry.links:
            if link.rel != "enclosure": continue

            local = os.path.basename(urllib.url2pathname(link.href))
            if not os.path.exists(local):
                try:
                    print "Getting", link.href, "as", local
                    urllib.urlretrieve(link.href, local, progress)
                except:
                    if (os.path.exists(local)): os.unlink(local)
                    raise
            link.href = publish + local

    # Merge the remote feed into the local feed
    #
    if os.path.exists("feed.xml"):
        fl = feedparser.parse("feed.xml")
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

    # Write out the local feed.
    #
    atomRoot = feedwriter.GetFeedElement(fl)
    ElementTree(atomRoot).write("feed.xml")

    rssRoot = rsswriter.GetFeedElement(fl)
    ElementTree(rssRoot).write("feed.rss")

config = ConfigParser.RawConfigParser()
config.read("feed.ini")
archiveFeed(config)
print "Done"

