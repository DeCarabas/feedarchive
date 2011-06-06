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
            SubElement(ae, "{http://www.w3.org/2005/Atom}name").text = detail.name
        if detail.has_key("href"):
            SubElement(ae, "{http://www.w3.org/2005/Atom}href").text = detail.href
        if detail.has_key("email"):
            SubElement(ae, "{http://www.w3.org/2005/Atom}email").text = detail.email

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
    root = SubElement(ee, "{http://www.w3.org/2005/Atom}source")
    TextElement(root, "{http://www.w3.org/2005/Atom}title", feed.title_detail)
    if feed.has_key("links"):
        for link in feed.links:
            LinkElement(root, "{http://www.w3.org/2005/Atom}link", link)
            
    TextElement(root, "{http://www.w3.org/2005/Atom}subtitle", feed.get("subtitle_detail"))
    TextElement(root, "{http://www.w3.org/2005/Atom}rights", feed.get("rights_detail"))
    SubElement(root, "{http://www.w3.org/2005/Atom}generator").text = "feedarchive"
    SubElement(root, "{http://www.w3.org/2005/Atom}updated").text = rfc3339(time.time())
    SubElementIf(root, "{http://www.w3.org/2005/Atom}id", feed.get("id"))
    
    if feed.has_key("image"):
        SubElement(root, "{http://www.w3.org/2005/Atom}icon").text = feed.image.href

    if feed.has_key("tags"):
        for tag in feed.tags:
            te = SubElement(root, "{http://www.w3.org/2005/Atom}category")
            if tag.get("term"): te.attrib["term"] = tag.term
            if tag.get("scheme"): te.attrib["scheme"] = tag.scheme
            if tag.get("label"): te.attrib["label"] = tag.label

    PersonElement(root, "{http://www.w3.org/2005/Atom}author", feed.get("author_detail"))


def GetFeedElement(id, source = None, entries = [], author = None, title = None, rights = None, image = None, tags = [], links = [], subtitle = None):
    """Create an atom:feed element for the provided feed, with the provided
    metadata dictionary.

    The provided feed must be in the format described at http://feedparser.org.
    """

    root = Element("{http://www.w3.org/2005/Atom}feed")
    TextElement(root, "{http://www.w3.org/2005/Atom}title", title)
    for link in links:
        LinkElement(root, "{http://www.w3.org/2005/Atom}link", link)
            
    TextElement(root, "{http://www.w3.org/2005/Atom}subtitle", subtitle)
    TextElement(root, "{http://www.w3.org/2005/Atom}rights", rights)
    SubElement(root, "{http://www.w3.org/2005/Atom}generator").text = "feedarchive"
    SubElement(root, "{http://www.w3.org/2005/Atom}updated").text = rfc3339(time.time())
    SubElementIf(root, "{http://www.w3.org/2005/Atom}id", id)
    
    if image:
        SubElement(root, "{http://www.w3.org/2005/Atom}icon").text = image.href

    for tag in tags:
        te = SubElement(root, "{http://www.w3.org/2005/Atom}category")
        if tag.get("term"): te.attrib["term"] = tag.term
        if tag.get("scheme"): te.attrib["scheme"] = tag.scheme
        if tag.get("label"): te.attrib["label"] = tag.label

    PersonElement(root, "{http://www.w3.org/2005/Atom}author", author)

    for entry in entries:
        ee = SubElement(root, "{http://www.w3.org/2005/Atom}entry")
        TextElement(ee, "{http://www.w3.org/2005/Atom}title", entry.get("title_detail"))
        if entry.has_key("links"):
            for link in entry.links:
                LinkElement(ee, "{http://www.w3.org/2005/Atom}link", link)
        TextElement(ee, "{http://www.w3.org/2005/Atom}summary", entry.get("summary_detail"))
        TextElement(ee, "{http://www.w3.org/2005/Atom}content", entry.get("content_detail"))
        DateTimeElement(ee, "{http://www.w3.org/2005/Atom}published", entry, "published")
        DateTimeElement(ee, "{http://www.w3.org/2005/Atom}updated", entry, "updated")
        SubElementIf(ee, "{http://www.w3.org/2005/Atom}id", entry.get("id"))
        PersonElement(ee, "{http://www.w3.org/2005/Atom}author", entry.get("author_detail"))
        PersonElement(ee, "{http://www.w3.org/2005/Atom}publisher", entry.get("publisher_detail"))
        if entry.has_key("contributors"):
            for contributor in entry.contributors:
                PersonElement(ee, "{http://www.w3.org/2005/Atom}contributor", contributor)
        if source:
            CreateSourceElement(ee, source)

    return root
