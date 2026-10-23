# Rags-Webscraper

A Wikipedia crawler. Records each page's title, URL and H2 headings.

## Setup
```
pip install -r requirements.txt
```
Edit `USER_AGENT` in `config.py` with your contact details with credit given please.

## Run
```
python Webcrawler.py                                   #saves to results.jsonl
python Webcrawler.py --firebase-key serviceAccount.json  #saves to Firestore
python Webcrawler.py --max-pages 50 --delay 2
(python3 if you're on mac)
```

## Firebase setup
1. Firebase console -> create a project -> Build -> **Firestore Database** -> Create database.
2. Project settings -> **Service accounts** -> *Generate new private key*. Save the JSON next to the scripts
   (it's git-ignored).
3. Run with `--firebase-key`. Results appear in the console under the `pages` collection.
