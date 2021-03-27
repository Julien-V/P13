# Séezlangues [![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![Maintenance](https://img.shields.io/badge/maintained%3F-yes-green.svg)](https://github.com/Julien-V/seezlangues/commits/master) [![Generic badge](https://img.shields.io/badge/coverage-87%25-green.svg)](https://github.com/Julien-V/seezlangues/)


SéezLangues est un site collaboratif, une plateforme guidée par une équipe d’une dizaine de professeurs de langues.
C’est à l’occasion d’une rencontre en 2020, entre professeurs, qu’une proposition est envisagée, celle de créer un support de partage de ressources pédagogiques.

## Installation

Ce projet utilise PostgreSQL.

### Python 3.7.3

```
$ python3 --version
Python 3.7.3
```

### Création de l'environnement virtuel et installation des dépendances
```
virtualenv P13
cd P13
source bin/activate
pip install -r requirements.txt
```
## Lancement

### Serveur de développement
```
./manage.py runserver
```
### Tests
```
pytest
```
