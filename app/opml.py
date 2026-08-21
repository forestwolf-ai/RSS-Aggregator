import xml.etree.ElementTree as ET
from app import db
from app.models import Source

def export_opml():
    """导出所有RSS源为OPML字符串"""
    opml = ET.Element('opml', version='1.0')
    head = ET.SubElement(opml, 'head')
    title = ET.SubElement(head, 'title')
    title.text = 'RSS Aggregator Feeds'
    body = ET.SubElement(opml, 'body')
    
    sources = Source.query.all()
    # 按分类分组
    categories = {}
    for s in sources:
        categories.setdefault(s.category, []).append(s)
    
    for cat, srcs in categories.items():
        outline = ET.SubElement(body, 'outline', text=cat, title=cat)
        for s in srcs:
            ET.SubElement(outline, 'outline', type='rss', text=s.name, title=s.name,
                          xmlUrl=s.url, htmlUrl=s.url)
    
    return ET.tostring(opml, encoding='unicode', xml_declaration=True)

def import_opml(opml_content):
    """从OPML字符串导入RSS源，返回成功和失败数量"""
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
            # 查找父级分类
            parent = outline.getparent()
            if parent is not None and parent.tag == 'outline' and parent.get('text'):
                category = parent.get('text')
            # 避免重复
            exists = Source.query.filter_by(url=xml_url).first()
            if exists:
                continue
            source = Source(name=name, url=xml_url, category=category)
            db.session.add(source)
            success += 1
        db.session.commit()
    except Exception as e:
        failed = 1
    return success, failed