# Voice2Picto

Voice2Picto est une application python permettant de transcrire la parole vers une suite de pictogrammes ARASAAC.
L'application utilise un outil de reconnaissance automatique de la parole, couplé à un modèle de désambiguïsation lexicale.

## Sommaire

* [Installation](#requirements)
* [Présentation de l'application](#presentation)
* [Version](#version)
* [Liens utiles](#links)

## Installation

1Créer un répertoire pictodemo et installer les modules nécessaires :
```
mkdir voice2picto
cd voice2picto
git clone https://github.com/macairececile/Voice2Picto.git
git clone https://github.com/macairececile/nwsd.git
```

2. Créer un environnement conda avec une version python=3.9 :
```
conda create -n voice2picto python=3.9
```

3. Installer les dépendances nécessaires :
```
conda activate voice2picto
cd voice2picto
pip install -r requirements.txt
```

4. Télécharger le modèle de désambiguïsation + pictogrammes ARASAAC, disponibles sur ce lien 
<https://cloud.univ-grenoble-alpes.fr/s/THqgCsd2WFpyzj7> et les extraire dans le répertoire pictodemo :
```
unzip model_wsd.zip -d /voice2picto
unzip ARASAAC_pictos.zip -d /voice2picto
```

## Présentation de l'application

L'interface se présente comme ceci :
![](/res/images/voice2picto1.png "Accueil")



