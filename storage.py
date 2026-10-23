"""firestore (viewable in the firebase console)"""
import hashlib
import json
from datetime import datetime, timezone
def doc_id_for(url):
    return hashlib.sha1(url.encode("utf-8")).hexdigest()
class JsonlStorage:
    def __init__(self, path="results.jsonl"):
        self._file = open(path, "a", encoding="utf-8")
    def save(self, record):
        self._file.write(json.dumps(record, ensure_ascii=False) + "\n")
        self._file.flush()
    def close(self):
        self._file.close()
class FirestoreStorage:
    def __init__(self, credentials_path, collection, batch_size=20):
        import firebase_admin
        from firebase_admin import credentials, firestore

        if not firebase_admin._apps:
            firebase_admin.initialize_app(credentials.Certificate(credentials_path))
        self._db = firestore.client()
        self._collection = self._db.collection(collection)
        self._batch_size = batch_size
        self._pending = []
    def save(self, record):
        self._pending.append(record)
        if len(self._pending) >= self._batch_size:
            self.flush()
    def flush(self):
        if not self._pending:
            return
        batch = self._db.batch()
        for record in self._pending:
            ref = self._collection.document(doc_id_for(record["url"]))
            batch.set(ref, record)
        batch.commit()
        self._pending = []
    def close(self):
        self.flush()
def make_record(page_number, url, title, headings):
    return {
        "page_number": page_number,
        "url": url,
        "title": title,
        "headings": headings,
        "heading_count": len(headings),
        "scraped_at": datetime.now(timezone.utc).isoformat(),
    }
