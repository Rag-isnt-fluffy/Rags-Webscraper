
from urllib.parse import urlparse, unquote, parse_qs

def should_skip_url(url):
    parsed = urlparse(url)
    path = unquote(parsed.path)
    if parsed.netloc.lower() != ALLOWED_DOMAIN:
        return True
    if not path.startswith("/wiki/"):
        return True
    title = path[len("/wiki/"):]
    if not title:
        return True
    if ":" in title:
        namespace = title.split(":", 1)[0]
        namespace = namespace.replace(" ", "_").lower()
        if namespace in BLOCKED_NAMESPACES:
            return True
    parameters = parse_qs(parsed.query)
    if BLOCKED_PARAMETERS.intersection(parameters):
        return True
    return False

#wkipedia namespaces to avoid
BLOCKED_NAMESPACES = {
    "special",
    "talk",
    "user",
    "user_talk",
    "wikipedia",
    "wikipedia_talk",
    "file",
    "file_talk",
    "mediawiki",
    "mediawiki_talk",
    "template",
    "template_talk",
    "help",
    "help_talk",
    "category",
    "category_talk",
    "portal",
    "portal_talk",
    "draft",
    "draft_talk",
}
BLOCKED_PARAMETERS = {
    "action",
    "oldid",
    "diff",
    "printable",
}
ALLOWED_DOMAIN = "en.wikipedia.org"
