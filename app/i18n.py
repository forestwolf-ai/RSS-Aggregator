TRANSLATIONS = {
    "en": {
        "app_name": "RSS Aggregator",
        "add_source": "Add Source",
        "delete_source": "Delete",
        "edit_source": "Edit",
        "refresh": "Refresh",
        "sources": "Sources",
        "articles": "Articles",
        "all": "All",
        "unread": "Unread",
        "settings": "Settings",
        "language": "Language",
        "interval": "Update Interval (minutes)",
        "save": "Save",
    },
    "zh": {
        "app_name": "RSS聚合器",
        "add_source": "添加源",
        "delete_source": "删除",
        "edit_source": "编辑",
        "refresh": "刷新",
        "sources": "源",
        "articles": "文章",
        "all": "全部",
        "unread": "未读",
        "settings": "设置",
        "language": "语言",
        "interval": "更新间隔（分钟）",
        "save": "保存",
    }
}

def translate(key, lang='en'):
    return TRANSLATIONS.get(lang, {}).get(key, key)