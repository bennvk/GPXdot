#!/bin/bash

gpxdot_fichier() {
    read -p "Nom du fichier de sortie (ex : Paris-Brest-Paris.txt) : " output
    echo ""
    echo " Conversion du fichier en cours ... "
    mkdir -p $HOME/gpxdot/Fichiers_texte
    python3 $HOME/gpxdot/gpxdot.py $HOME/gpxdot/$fichier_gpx $distance > $HOME/gpxdot/Fichiers_texte/$output
    echo ""
    echo " Fichier copié dans le répertoire $HOME/gpxdot/$output"
}

gpxdot_sansfichier() {
    echo ""
    echo "Conversion du fichier en cours ..."
    python3 $HOME/gpxdot/gpxdot.py $HOME/gpxdot/$fichier_gpx $distance
}

echo ""

while true; do
    read -p "Fichier à convertir : " fichier_gpx
    if [[ -f "$HOME/gpxdot/$fichier_gpx" ]]; then
        break
    else
        echo "Erreur : fichier introuvable dans $HOME/gpxdot/$fichier_gpx. Réessayez."
    fi
done

read -p "Distance entre les points (en mètres) : " distance

read -p "Voulez-vous rediriger la sortie dans un fichier ? [O/n]" choix_fichier

case $choix_fichier in
    [0Oo]) gpxdot_fichier
           ;;
    [Non]) gpxdot_sansfichier
           ;;
    *) echo "Choix non valide, veuillez réessayer"
       exit 1
       ;;
esac