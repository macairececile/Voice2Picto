# Voice2Picto

Voice2Picto est une application python permettant de transcrire la parole vers une suite de pictogrammes ARASAAC.
L'application utilise un outil de reconnaissance automatique de la parole, couplé à un modèle de désambiguïsation
lexicale.

## Sommaire

* [Installation](#installation)
* [Présentation de l'application](#presentation_app)
* [Lien utiles](#liens_utiles)

## Installation

1. Créer un répertoire pictodemo et installer les modules nécessaires :

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
   <https://cloud.univ-grenoble-alpes.fr/s/THqgCsd2WFpyzj7> et les extraire dans le répertoire voice2picto :

```
unzip model_wsd.zip -d /voice2picto
unzip ARASAAC_pictos.zip -d /voice2picto
```

## Présentation de l'application <a name="presentation_app"></a>

L'interface se présente comme ceci : </br>

![](/res/images/voice2picto1.png "Accueil")

* _**Sélection du mode**_ / permet de choisir entre deux modes :
    * "Appuyez pour parler" qui enregistre et transcrit la voix au clique du bouton microphone.
    * "Détection de l'activité" qui enregistre puis transcrit la voix en fonction d'un seuil d'intensité de voix, défini
      par "Seuil d'énergie".
* _**Sélection du microphone**_ / pour choisir le microphone à utiliser pour enregistrer la voix.
* _**Exit**_ pour quitter l'application.

Lorsque l'enregistrement de votre voix est terminée, le deuxième encadré affichera deux infos :

1. "Parole reçue" qui retranscrira ce qui a été dit (si aucun texte n'est affiché, il est préférable de changer de
   micro).
2. "Traduction en cours ...".

Une fois la traduction terminée, l'encadré de droite affichera le temps de décodage de la voix vers les pictogrammes en
secondes. </br>
La traduction sera présentée dans le premier encadré. Pour chaque picto présenté, nous affichons également le mot par
lequel il est défini.

La liste des erreurs contenues dans la traduction proposée n'est pas exhaustive, mais en voici quelques exemples :

- mot non traduit (car celui-ci n'est pas disponible dans la base Arasaac),
- mot ne correspondant pas exactement au sens du mot,
- mot incorrect car la transcription de la parole est erronée.

## Lien utiles <a name="liens_utiles"></a>

Le système de reconnaissance automatique de la parole est basé sur la boîte à outils Kaldi. </br>
Le système de désambiguïsation s'appuie sur le toolkit <https://github.com/getalp/disambiguate> implémenté en python. </br>
La banque de pictogrammes utilisée est [ARASAAC](https://arasaac.org/). </br>

Pour toutes informations, vous pouvez nous contacter par [mail](cecile.macaire@univ-grenoble-alpes.fr).
