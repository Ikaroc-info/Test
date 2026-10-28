#!/usr/bin/env python3
"""Transfère des playlists Spotify vers YouTube Music.

Exemples :
    python transfer.py --list                       # liste vos playlists Spotify
    python transfer.py --playlist "Ma playlist"     # transfère une playlist (nom, ID ou lien)
    python transfer.py --all                        # transfère toutes vos playlists
    python transfer.py --liked                      # transfère vos titres likés
    python transfer.py --all --dry-run              # simule sans rien créer
"""

import argparse
import os
import re
import sys
import time

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from ytmusicapi import YTMusic

SPOTIFY_SCOPES = "playlist-read-private playlist-read-collaborative user-library-read"
BATCH_SIZE = 50


# --- Spotify ----------------------------------------------------------------

def spotify_client():
    for var in ("SPOTIPY_CLIENT_ID", "SPOTIPY_CLIENT_SECRET"):
        if not os.environ.get(var):
            sys.exit(f"Variable d'environnement manquante : {var} (voir README.md)")
    os.environ.setdefault("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8888/callback")
    return spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SPOTIFY_SCOPES, open_browser=True))


def paginate(sp, page):
    while page:
        yield from page["items"]
        page = sp.next(page) if page.get("next") else None


def spotify_playlists(sp):
    return list(paginate(sp, sp.current_user_playlists(limit=50)))


def track_from_item(item):
    # L'API renvoie l'objet sous "track" (ou "item" dans les versions récentes).
    t = item.get("track") or item.get("item")
    if not t or t.get("type", "track") != "track" or t.get("is_local"):
        return None
    return {
        "title": t["name"],
        "artists": [a["name"] for a in t.get("artists", [])],
        "album": (t.get("album") or {}).get("name", ""),
        "duration": (t.get("duration_ms") or 0) // 1000,
    }


def spotify_tracks(sp, playlist_id):
    items = paginate(sp, sp.playlist_items(playlist_id, limit=100, additional_types=("track",)))
    return [t for t in map(track_from_item, items) if t]


def spotify_liked_tracks(sp):
    return [t for t in map(track_from_item, paginate(sp, sp.current_user_saved_tracks(limit=50))) if t]


def resolve_playlist(playlists, query):
    m = re.search(r"playlist[/:]([A-Za-z0-9]+)", query)
    pid = m.group(1) if m else query
    for p in playlists:
        if p["id"] == pid or p["name"].lower() == query.lower():
            return p
    return None


# --- YouTube Music ----------------------------------------------------------

def normalize(s):
    s = re.sub(r"\(.*?\)|\[.*?\]", "", s.lower())
    s = re.sub(r"\s-\s.*(remaster|version|edit|live|mix).*", "", s)
    return re.sub(r"[^\w\s]", "", s).strip()


def score(track, result):
    """Note de 0 à ~4 : titre, artiste, durée."""
    s = 0.0
    title, rtitle = normalize(track["title"]), normalize(result.get("title") or "")
    if title == rtitle:
        s += 2
    elif title in rtitle or rtitle in title:
        s += 1
    rartists = " ".join(a["name"].lower() for a in result.get("artists") or [])
    if any(a.lower() in rartists for a in track["artists"]):
        s += 1.5
    rdur = result.get("duration_seconds")
    if rdur and track["duration"] and abs(rdur - track["duration"]) <= 5:
        s += 0.5
    return s


def find_on_ytmusic(yt, track):
    query = f"{track['title']} {' '.join(track['artists'][:2])}"
    best, best_score = None, 0.0
    for filt in ("songs", "videos"):
        try:
            results = yt.search(query, filter=filt, limit=5)
        except Exception as e:
            print(f"    ! erreur de recherche : {e}")
            continue
        for r in results:
            if not r.get("videoId"):
                continue
            sc = score(track, r)
            if sc > best_score:
                best, best_score = r, sc
        if best_score >= 3:  # bon match parmi les "songs", inutile de chercher les vidéos
            break
    return best["videoId"] if best and best_score >= 1.5 else None


def transfer(yt, name, tracks, description, privacy, dry_run):
    print(f"\n== {name} ({len(tracks)} titres)")
    video_ids, missing = [], []
    for i, t in enumerate(tracks, 1):
        label = f"{', '.join(t['artists'])} - {t['title']}"
        vid = find_on_ytmusic(yt, t)
        print(f"  [{i}/{len(tracks)}] {'OK ' if vid else '-- '} {label}")
        if vid and vid not in video_ids:
            video_ids.append(vid)
        elif not vid:
            missing.append(label)

    if dry_run:
        print(f"  (simulation) {len(video_ids)} trouvés, {len(missing)} introuvables")
    elif video_ids:
        pid = yt.create_playlist(name, description, privacy_status=privacy,
                                 video_ids=video_ids[:BATCH_SIZE])
        if not isinstance(pid, str):
            raise RuntimeError(f"Création de la playlist échouée : {pid}")
        for start in range(BATCH_SIZE, len(video_ids), BATCH_SIZE):
            yt.add_playlist_items(pid, video_ids[start:start + BATCH_SIZE], duplicates=True)
            time.sleep(1)
        print(f"  -> https://music.youtube.com/playlist?list={pid}")

    if missing:
        fname = "introuvables_" + re.sub(r"[^\w-]+", "_", name) + ".txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write("\n".join(missing) + "\n")
        print(f"  {len(missing)} titre(s) introuvable(s), liste dans {fname}")


# --- main -------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Spotify -> YouTube Music")
    ap.add_argument("--list", action="store_true", help="lister les playlists Spotify")
    ap.add_argument("--playlist", action="append", default=[], metavar="NOM|ID|LIEN",
                    help="playlist à transférer (option répétable)")
    ap.add_argument("--all", action="store_true", help="transférer toutes les playlists")
    ap.add_argument("--liked", action="store_true", help="transférer les titres likés")
    ap.add_argument("--privacy", default="PRIVATE", choices=["PRIVATE", "UNLISTED", "PUBLIC"])
    ap.add_argument("--auth", default="browser.json", help="fichier d'auth ytmusicapi")
    ap.add_argument("--dry-run", action="store_true", help="chercher sans créer de playlist")
    args = ap.parse_args()

    sp = spotify_client()
    playlists = spotify_playlists(sp)

    if args.list or not (args.playlist or args.all or args.liked):
        for p in playlists:
            total = (p.get("tracks") or p.get("items") or {}).get("total", "?")
            print(f"{p['id']}  {total:>5}  {p['name']}")
        return

    if not os.path.exists(args.auth):
        sys.exit(f"Fichier {args.auth} introuvable : lancez d'abord `ytmusicapi browser` (voir README.md)")
    yt = YTMusic(args.auth)

    selected = playlists if args.all else []
    for q in args.playlist:
        p = resolve_playlist(playlists, q)
        if p:
            selected.append(p)
        else:
            print(f"Playlist introuvable : {q}")

    for p in selected:
        transfer(yt, p["name"], spotify_tracks(sp, p["id"]),
                 f"Importée depuis Spotify. {p.get('description') or ''}".strip(),
                 args.privacy, args.dry_run)
    if args.liked:
        transfer(yt, "Titres likés (Spotify)", spotify_liked_tracks(sp),
                 "Importée depuis Spotify", args.privacy, args.dry_run)


if __name__ == "__main__":
    main()
