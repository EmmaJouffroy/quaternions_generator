# Création de la base de données

Le projet suivant consiste en la réalisation d'une base de données d'images en 128*128. Ce dossier contient un jupyter notebook permettant de visualiser l'ensemble de l'espace recouvert pour les rotations, un fichier blender permettant de générer les images et un script python contenant l'ensemble des fonctions utiles à la création des images.

# Installation

Requis: Python 3.7+ | Linux, Mac OS X, Windows

```sh
pip install virtualenv
```
Puis dans le dossier du projet:  

```sh
source venv/bin/activate
```
Lancer cette commande activera l'environnement virtuel, dans lequel l'ensemble des paquets nécessaires au projet sont placés. 
Si le venv n'est pas téléchargé (fichier trop volumineux), alors lancer la commande suivante : 

```sh
pip install -r requirements.txt
```

Cela permet d'installer les paquets et les librairies dans les versions nécessaires. 

# Préparez-vous :

Pour lancer le notebook principal se lance:
```sh
jupyter notebook
```
Puis sélectionner space_visualisation.ipynb !

# Description

Ce dossier contient l'ensemble des fichiers nécessaires pour la création de la base de données et une explication de cette dernière. Le résultat final obtenu est le suivant :


<p float="left">
<img src="img/output_min.gif" width=500 height="400"/>
<img src="img/rotating_object_min.gif" width=320 height="300"/>
<p/>
