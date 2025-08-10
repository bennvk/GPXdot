#!bin/bash

echo ""

while true; do
    read -p "Fichier à convertir : " fichier_gpx
    if [[ -f "$HOME/gpxdot/$fichier" ]]; then
        break
    else
        echo "Erreur : fichier introuvable dans $HOME/gpxdot/$fichier. Réessayez."
    fi

read -p "Distance entre les points (en mètres) : " distance

case $choix_fichier in
    [0Oo]) gpxdot_fichier
           ;;
    [Non]) gpxdot_sansfichier
           ;;
    *) echo "Choix non valide, veuillez réessayer"
       exit 1
       ;;

gpxdot_fichier() {
    read -p "Nom du fichier de sortie (ex : Paris-Brest-Paris.txt) : " output
    echo ""
    echo " Conversion du fichier en cours ... "
    mkdir -p ~/gpxdot/Fichiers_texte
    python3 ~/gpxdot/gpxdot.py ~/gpxdot/$fichier $distance > ~/gpxdot/Fichiers_texte/$output
    echo ""
    echo " Fichier copié dans le répertoire $HOME/gpxdot/$output"
}

gpxdot_sansfichier() {
    echo ""
    echo "Conversion du fichier en cours ..."
    python3 ~/gpxdot/gpxdot.py ~/gpxdot/$fichier $distance
}