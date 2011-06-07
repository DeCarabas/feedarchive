# Write out an atom feed for the in-memory format described here:
# http://feedparser.org/
#
from elementtree.ElementTree import Element, SubElement, ElementTree
from rfc3339 import rfc3339
import time

def TextElement(root, name, detail_value):
    if detail_value:
        te = SubElement(root, name)
        if detail_value.type == "text/html": detail_value.type = "html"
        if detail_value.type == "text/plain": detail_value.type = "text"
        te.attrib["type"] = detail_value.type
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
        ae = SubElement(root, name)
        if detail.has_key("name"):
            SubElement(ae, "name").text = detail.name
        if detail.has_key("href"):
            SubElement(ae, "href").text = detail.href
        if detail.has_key("email"):
            SubElement(ae, "email").text = detail.email

def SubElementIf(root, name, text):
    if text:
        SubElement(root, name).text = text

def DateTimeElement(root, name, element, key):
    if element.has_key(key + "_parsed"):
        SubElementIf(root, name, rfc3339(time.mktime(element[key + "_parsed"])))
    else:
        SubElementIf(root, name, element.get(key))

def CreateSourceElement(ee, feed):
    """Create an atom:source element in the provided entry element,
    based on the provided feed metadata.
    """
    if not feed: return
    
    root = SubElement(ee, "source")
    TextElement(root, "title", feed.get("title_detail"))
    if feed.has_key("links"):
        for link in feed.links:
            LinkElement(root, "link", link)
            
    TextElement(root, "subtitle", feed.get("subtitle_detail"))
    TextElement(root, "rights", feed.get("rights_detail"))
    SubElement(root, "generator").text = "feedarchive"
    SubElement(root, "updated").text = rfc3339(time.time())
    SubElementIf(root, "id", feed.get("id"))
    
    if feed.has_key("image"):
        SubElement(root, "icon").text = feed.image.href

    if feed.has_key("tags"):
        for tag in feed.tags:
            te = SubElement(root, "category")
            if tag.get("term"): te.attrib["term"] = tag.term
            if tag.get("scheme"): te.attrib["scheme"] = tag.scheme
            if tag.get("label"): te.attrib["label"] = tag.label

    PersonElement(root, "author", feed.get("author_detail"))


def GetFeedElement(feed):
    """Create an atom:feed element for the provided feed.

    The provided feed must be in the format described at http://feedparser.org.
    """

    root = Element("feed")
    root.attrib["xmlns"] = "http://www.w3.org/2005/Atom"

    TextElement(root, "title", feed.feed.get("title_detail"))
    if feed.feed.has_key("links"):
        for link in feed.feed.links:
            LinkElement(root, "link", link)
            
    TextElement(root, "subtitle", feed.feed.get("subtitle_detail"))
    TextElement(root, "rights", feed.feed.get("rights_detail"))
    SubElement(root, "generator").text = "feedarchive"
    SubElement(root, "updated").text = rfc3339(time.time())
    SubElementIf(root, "id", feed.feed.get("id"))
    
    if feed.feed.has_key("image"):
        SubElement(root, "icon").text = feed.feed.image.href

    if feed.feed.has_key("tags"):
        for tag in feed.feed.tags:
            te = SubElement(root, "category")
            if tag.get("term"): te.attrib["term"] = tag.term
            if tag.get("scheme"): te.attrib["scheme"] = tag.scheme
            if tag.get("label"): te.attrib["label"] = tag.label

    PersonElement(root, "author", feed.feed.get("author_detail"))

    for entry in feed.entries:
        ee = SubElement(root, "entry")
        TextElement(ee, "title", entry.get("title_detail"))
        if entry.has_key("links"):
            for link in entry.links:
                LinkElement(ee, "link", link)
        TextElement(ee, "summary", entry.get("summary_detail"))
        TextElement(ee, "content", entry.get("content_detail"))
        DateTimeElement(ee, "published", entry, "published")
        DateTimeElement(ee, "updated", entry, "updated")
        SubElementIf(ee, "id", entry.get("id"))
        PersonElement(ee, "author", entry.get("author_detail"))
        PersonElement(ee, "publisher", entry.get("publisher_detail"))
        if entry.has_key("contributors"):
            for contributor in entry.contributors:
                PersonElement(ee, "contributor", contributor)
        CreateSourceElement(ee, entry.get("source"))

    return root
