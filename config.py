from urllib.parse import urlparse, unquote, parse_qs

STARTING_URL = "https://en.wikipedia.org/wiki/Main_Page"
MAX_PAGES = 1000
REQUEST_DELAY = 1.0
TIMEOUT = 10       
USER_AGENT = "RagsWebscraper/0.1 (https://github.com/RagtheGreat/Rags-Webscraper; RagtheGreat@hotmail.com). MAY BE USED BY A THIRD PARTY, DO NOT SPAM WIKIPEDIA."
FIRESTORE_COLLECTION = "pages"
FIRESTORE_BATCH_SIZE = 20

ALLOWED_DOMAIN = "en.wikipedia.org"
BLOCKED_NAMESPACES = {
    "special", "talk", "user", "user_talk", "wikipedia", "wikipedia_talk",
    "file", "file_talk", "mediawiki", "mediawiki_talk", "template",
    "template_talk", "help", "help_talk", "category", "category_talk",
    "portal", "portal_talk", "draft", "draft_talk",
}
BLOCKED_PARAMETERS = {"action", "oldid", "diff", "printable"}


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
        namespace = title.split(":", 1)[0].replace(" ", "_").lower()
        if namespace in BLOCKED_NAMESPACES:
            return True
    if BLOCKED_PARAMETERS.intersection(parse_qs(parsed.query)):
        return True
    return False
