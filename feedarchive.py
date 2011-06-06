# Archives a feed. Pulls from the source, saves appropriate resources.
# Not terribly complete, but perhaps sufficient.
#
from elementtree.ElementTree import ElementTree
import feedwriter
import feedparser
import urllib
import os.path
import sys

# Download the feed and also its enclosures.
#
def progress(blocks, size, fileSize):
    bytes = blocks * size
    percent = (float(bytes) / float(fileSize))
    sys.stdout.write("[%-40s] %d%% (%d/%d)\r" % ('='*int(40*percent), (percent * 100.0), bytes, fileSize))

fr = feedparser.parse("http://www.bigcontact.com/latw/rss")
for entry in fr.entries:
    for link in entry.links:
        if link.rel != "enclosure": continue

        local = os.path.basename(urllib.url2pathname(link.href))
        print "Getting", link.href, "as", local

#        h.request(link.href, "GET")

#        urllib.urlretrieve(link.href, local, progress)
#        link.href = local

# Merge the remote feed into the local feed
#
if os.path.exists("feed.xml"):
    fl = feedparser.parse("feed.xml")
    em = dict([(e.id, True) for e in fl.entries])
    for entry in fr.entries:
        if not em.has_key(entry.id):
            fl.entries.append(entry)
else:
    fl = fr

# Write out the local feed.
#
atomRoot = feedwriter.GetFeedElement("tag:jddoty@gmail.com", source=fl.feed, entries=fl.entries)
ElementTree(atomRoot).write("feed.xml")
