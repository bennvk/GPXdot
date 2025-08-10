#bin/bash

echo ""
read -p "Fichier à convertir : " fichier || echo "Fichier introuvable"
read -p "Distance entre les points (en mètres) : " distance || echo "Distance entrée invalide"
read -p "Rediriger la sortie dans un fichier ? [O/n]" filed

if [[ $filed == "O" || $filed == "0" || $filed == "o" ]]; then
    read -p "Nom du fichier de sortie : " output
    echo ""
    echo " Conversion du fichier en cours ... "
    mkdir -p ~/gpxdot/Fichiers_texte
    python3 ~/gpxdot/gpxdot.py ~/gpxdot/$fichier $distance > ~/gpxdot/Fichiers_texte/$output
    echo ""
    echo " Fichier texte copié dans le répertoire /home/olivier/gpxdot/$output "
else
    echo ""
    echo "Conversion du fichier en cours ..."
    python3 ~/gpxdot/gpxdot.py ~/gpxdot/$fichier $distance
fi