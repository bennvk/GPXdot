# GPXdot, transformer un gpx en liste de coordonnées


## Installation

### Cloner le dépôt

```python
git clone https://github.com/<ton-user>/gpxdot-gui.git
cd gpxdot-gui
```

### Créer un environnement virtuel (optionnel mais recommandé)

```python
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
venv\\Scripts\\activate    # Windows
```

### Installer les dépendances

```python
pip install gpxpy geopy
```

## Utilisation

Lancer l’application :

```python
python3 gpxdot_gui_github_dark.py
```

- Choisissez un fichier .gpx (dossier par défaut : ~/gpxdot/gpxFiles).
- Indiquez la distance minimale entre les points.
- Optionnel : cochez Enregistrer la sortie dans un fichier (stockage dans ~/gpxdot/txtFiles).
- Cliquez sur Lancer et suivez la progression.
