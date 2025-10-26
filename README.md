# GPXdot, transformer un gpx en liste de coordonnées


## Installation

### Cloner le dépôt

```python
git clone https://github.com/bennvk/gpxdot.git
cd gpxdot
```

### Créer un environnement virtuel (optionnel mais recommandé)

```bash
python3 -m venv venv
source venv/bin/activate
```

### Installer les dépendances

```bash
pip install -r requirements.txt
```

## Utilisation

Lancer l’application :

```bash
python3 gpxdot-gui.py
```

- Choisissez un fichier .gpx (dossier par défaut : ~/gpxdot/gpxFiles).
- Indiquez la distance minimale entre les points.
- Optionnel : cochez Enregistrer la sortie dans un fichier (stockage dans ~/gpxdot/txtFiles).
- Cliquez sur Lancer et suivez la progression.

## Arborescence recommandée

```text
~/gpxdot/
│── gpxFiles/
│── txtFiles/
│── gpxdot-gui.py
```
