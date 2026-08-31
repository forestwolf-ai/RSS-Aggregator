import xml.etree.ElementTree as ET
import logging
from app import db
from app.models import Source

logger = logging.getLogger(__name__)

def export_opml():
    opml = ET.Element('opml', version='1.0')
    head = ET.SubElement(opml, 'head')
    title = ET.SubElement(head, 'title')
    title.text = 'RSS Aggregator Feeds'
    body = ET.SubElement(opml, 'body')

    sources = Source.query.all()
    categories = {}
    for s in sources:
        categories.setdefault(s.category or 'General', []).append(s)

    for cat, srcs in categories.items():
        outline = ET.SubElement(body, 'outline', text=cat, title=cat)
        for s in srcs:
            ET.SubElement(outline, 'outline', type='rss', text=s.name, title=s.name,
                          xmlUrl=s.url, htmlUrl=s.url)
    return ET.tostring(opml, encoding='unicode', xml_declaration=True)

def import_opml(opml_content):
    success = 0
    failed = 0
    try:
        root = ET.fromstring(opml_content)
        for outline in root.iter('outline'):
            xml_url = outline.get('xmlUrl')
            if not xml_url:
                continue
            name = outline.get('text') or outline.get('title') or xml_url
            category = 'Imported'
            parent = outline.getparent()
            if parent is not None and parent.tag == 'outline' and parent.get('text'):
                category = parent.get('text')
            if Source.query.filter_by(url=xml_url).first():
                continue
            source = Source(name=name, url=xml_url, category=category)
            db.session.add(source)
            success += 1
        db.session.commit()
    except Exception as e:
        logger.error(f"OPML import error: {e}")
        failed = 1
        db.session.rollback()
    return success, failed
