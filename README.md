# Spotify → YouTube Music

Script Python qui copie vos playlists Spotify (et vos titres likés) vers YouTube Music.
Pour chaque titre, il cherche « titre + artiste » sur YouTube Music et garde le meilleur résultat
(comparaison du titre, de l'artiste et de la durée). Les titres non trouvés sont listés dans
un fichier `introuvables_<playlist>.txt`.

## 1. Installation

Il faut Python 3.9 ou plus récent.

```bash
pip install -r requirements.txt
```

## 2. Accès à Spotify

1. Allez sur https://developer.spotify.com/dashboard et créez une application (« Create app »).
2. Dans **Redirect URIs**, ajoutez exactement : `http://127.0.0.1:8888/callback`
3. Cochez **Web API**, enregistrez, puis copiez le *Client ID* et le *Client Secret*.
4. Définissez-les dans votre terminal :

   ```bash
   # macOS / Linux
   export SPOTIPY_CLIENT_ID="votre_client_id"
   export SPOTIPY_CLIENT_SECRET="votre_client_secret"
   ```
   ```powershell
   # Windows (PowerShell)
   $env:SPOTIPY_CLIENT_ID="votre_client_id"
   $env:SPOTIPY_CLIENT_SECRET="votre_client_secret"
   ```

À la première utilisation, une page Spotify s'ouvre pour autoriser l'accès.

> Selon les règles actuelles de Spotify, les applications en « mode développement » peuvent
> exiger un compte Premium, et seuls les comptes ajoutés dans *User Management* peuvent s'y connecter.

## 3. Accès à YouTube Music

1. Ouvrez https://music.youtube.com dans votre navigateur, connecté à votre compte.
2. Ouvrez les outils de développement (F12), onglet **Réseau / Network**.
3. Cliquez n'importe où dans YouTube Music, puis cherchez une requête nommée `browse` (méthode POST).
4. Copiez ses **en-têtes de requête** (Request Headers) :
   - Chrome / Edge : clic droit sur la requête → *Copy* → *Copy request headers*
   - Firefox : clic droit → *Copier la valeur* → *Copier les en-têtes de la requête*
5. Dans le terminal, lancez :

   ```bash
   ytmusicapi browser
   ```
   Collez les en-têtes, puis validez (Entrée, puis Ctrl+D sous macOS/Linux ou Ctrl+Z puis Entrée sous Windows).
   Cela crée le fichier `browser.json` dans le dossier.

⚠️ `browser.json` donne accès à votre compte Google : ne le partagez pas (il est ignoré par git).
Il reste valable tant que vous ne vous déconnectez pas de YouTube Music dans ce navigateur.

## 4. Utilisation

```bash
python transfer.py --list                          # voir vos playlists Spotify
python transfer.py --playlist "Ma playlist"        # une playlist (nom, ID ou lien Spotify)
python transfer.py --playlist "A" --playlist "B"   # plusieurs playlists
python transfer.py --all                           # toutes vos playlists
python transfer.py --liked                         # vos titres likés
python transfer.py --all --dry-run                 # tester sans rien créer
python transfer.py --all --privacy PUBLIC          # PRIVATE (défaut), UNLISTED ou PUBLIC
```

## Limites

- `ytmusicapi` n'est pas une API officielle de Google : elle peut cesser de fonctionner
  si YouTube change son site (mettez-la à jour avec `pip install -U ytmusicapi`).
- La correspondance est automatique : quelques titres peuvent être remplacés par une autre version
  (live, remix…). Vérifiez le fichier `introuvables_*.txt` et ajoutez les manquants à la main.
- Les fichiers locaux et les podcasts Spotify sont ignorés.
