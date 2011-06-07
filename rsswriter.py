# Write out an RSS 2.0 feed for the in-memory format described here:
# http://feedparser.org/
#
from elementtree.ElementTree import Element, SubElement, ElementTree
from rfc3339 import rfc3339
import time

def TextElement(root, name, detail_value):
    if detail_value:
        te = SubElement(root, name)
        te.text = detail_value.value

def LinkElement(root, name, link):
    if link:
        le = SubElement(root, name)
        if (link.has_key("rel")): le.attrib["rel"] = link.rel
        if (link.has_key("title")): le.attrib["title"] = link.title
        if (link.has_key("type")):
            le.attrib["type"] = link.type
        if (link.has_key("href")): le.attrib["href"] = link.href
    
def PersonElement(root, name, detail):
    if detail:
        SubElementIf(root, name, detail.get("email"))

def AttribIf(elem, name, text):
    if text:
        elem.attrib[name] = text

def SubElementIf(root, name, text):
    if text:
        SubElement(root, name).text = text

def DateTimeElement(root, name, element, key):
    if element.has_key(key + "_parsed"):
        SubElementIf(root, name, rfc3339(time.mktime(element[key + "_parsed"])))
    else:
        SubElementIf(root, name, element.get(key))

def GetFeedElement(feed):
    """Create an atom:feed element for the provided feed.

    The provided feed must be in the format described at http://feedparser.org.
    """

    rss = Element("rss")
    rss.attrib["version"] = "2.0"

    root = SubElement(rss, "channel")

    TextElement(root, "title", feed.feed.get("title_detail"))
    SubElementIf(root, "link", feed.feed.get("link"))
    
    TextElement(root, "description", feed.feed.get("subtitle_detail"))
    TextElement(root, "copyright", feed.feed.get("rights_detail"))
    SubElement(root, "generator").text = "feedarchive"
    
    if feed.feed.has_key("image"):
        im = feed.feed.image
        ie = SubElement(root, "image")
        SubElementIf(ie, "url", image.get("href"))
        SubElementIf(ie, "title", image.get("title"))
        SubElementIf(ie, "link", image.get("link"))

    if feed.feed.has_key("tags"):
        for tag in feed.feed.tags:
            te = SubElement(root, "category")
            if (tag.has_key("scheme")): te.attrib["domain"] = tag.scheme
            te.text = tag.term

    for entry in feed.entries:
        ee = SubElement(root, "item")
        TextElement(ee, "title", entry.get("title_detail"))
        SubElementIf(ee, "link", entry.get("link"))
        TextElement(ee, "description", entry.get("summary_detail"))
        SubElementIf(ee, "guid", entry.get("id"))
        DateTimeElement(ee, "pubDate", entry, "published")
        PersonElement(ee, "author", entry.get("author_detail"))

        if entry.has_key("links"):
            for link in entry.links:
                if link.rel != "enclosure": continue
                ence = SubElement(ee, "enclosure")
                AttribIf(ence, "url", link.get("url"))
                AttribIf(ence, "length", link.get("length"))
                AttribIf(ence, "type", link.get("type"))
                
    return rss
