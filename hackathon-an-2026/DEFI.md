# Parlementia

### Nom du défi
Parlementia — Copilote de prospective parlementaire

### Description courte
Un copilote qui aide les élus à construire des futurs souhaitables et à réaliser
le backcasting de leurs décisions politiques, en cohérence avec les 17 Objectifs
de Développement Durable (ODD).

### Porteur
Johnatan Ayoun

### Description longue
Parlementia part d'une intention politique ou législative exprimée par
l'utilisateur (objectif, leviers d'action, indicateurs de réussite, territoire
concerné, ODD prioritaires) et orchestre une chaîne de 9 agents pour produire
une analyse prospective complète :

1. **Compréhension** — cadrage de l'intention par 5 questions ciblées, puis
   reformulation soumise à validation (l'utilisateur peut la corriger avant de
   lancer l'analyse).
2. **Diagnostic systémique & juridique** — mise en contexte et jurisprudence.
3. **Recueil des données** — recherche de jeux de données pertinents via
   l'API publique data.gouv.fr.
4. **Scénarios prospectifs** — 3 scénarios à horizon 10 ans (réaliste,
   optimiste, pessimiste).
5. **Analyse au prisme des ODD** — score d'impact (0-100) de chaque scénario
   sur les 17 ODD, restitué sous forme de diagrammes radar.
6. **Évaluation scientifique** de la réalisation des scénarios.
7. **Recommandations d'arbitrage**.
8. **Contre-analyse critique** par un expert.
9. **Synthèse** — document parlementaire final, avec radars ODD.

L'outil reste strictement neutre : il n'éclaire pas pour convaincre, mais pour
décider. La couche LLM est interchangeable (Mistral API, Ollama en local et
souverain, ou mode simulé sans dépendance réseau) via une seule variable
d'environnement.

### Image principale
![Image principale](images/cover.png)

### Contributeurs
- Tiphaine Lalonde
- Mathieu Tank
- Marine Baron
- Sophie Nizart
- Dylan Lounis
- Joëlle Koundé
- Caroline Henry
- Salim Hassanaly

### Ressources utilisées
Cochez les ressources utilisées en remplaçant `[ ]` par `[x]`.

- [ ] `openfisca-france-parameters` — Base de données de paramètres ✺ OpenFisca
- [x] `an-dossiers-legislatifs` — Dossiers législatifs de l'Assemblée nationale (législature courante) ✺ Assemblée nationale
- [ ] `an-amendements-xvii` — Amendements déposés à l'Assemblée nationale (législature actuelle) ✺ Assemblée nationale
- [ ] `an-comptes-rendus` — Comptes rendus de la séance publique à l'Assemblée nationale (législature actuelle) ✺ Assemblée nationale
- [ ] `an-votes-xvii` — Votes des députés (législature actuelle) ✺ Assemblée nationale
- [ ] `an-deputes-en-exercice` — Députés en exercice ✺ Assemblée nationale
- [ ] `an-deputes-historique` — Historique des députés ✺ Assemblée nationale
- [ ] `an-deputes-senateurs-ministres-par-legislature` — Députés, sénateurs et ministres d'une législature ✺ Assemblée nationale
- [ ] `an-agenda-reunions` — Agenda des réunions à l'Assemblée nationale (législature courante) ✺ Assemblée nationale
- [ ] `an-questions-gouvernement` — Questions de l'Assemblée nationale au Gouvernement ✺ Assemblée nationale
- [ ] `an-questions-gouvernement-ecrites` — Questions écrites de l'Assemblée nationale au Gouvernement ✺ Assemblée nationale
- [ ] `an-questions-gouvernement-orales` — Questions orales de l'Assemblée nationale au Gouvernement ✺ Assemblée nationale
- [ ] `premier-ministre-legi` — Codes, lois et règlements consolidés ✺ Premier ministre
- [ ] `premier-ministre-dole` — Dossiers législatifs Légifrance ✺ Premier ministre
- [ ] `premier-ministre-jorf` — Édition ''Lois et décrets'' du Journal officiel ✺ Premier ministre
- [ ] `senat-dispositifs-textes` — Dispositifs des textes déposés ou adoptés au Sénat ✺ Sénat
- [ ] `senat-dossiers-legislatifs` — Dossiers législatifs du Sénat ✺ Sénat
- [ ] `senat-amendements` — Amendements déposés au Sénat ✺ Sénat
- [ ] `senat-senateurs` — Sénateurs ✺ Sénat
- [ ] `senat-questions-gouvernement` — Questions orales et écrites du Sénat au Gouvernement ✺ Sénat
- [ ] `senat-comptes-rendus` — Comptes rendus de la séance publique au Sénat ✺ Sénat
- [ ] `an-et-co-database-regroupement-toutes-donnees` — Base de données unifiée Parlement / Législation / Service Public ✺ Assemblée nationale & communauté
- [ ] `an-et-co-serveur-mcp-regroupement-toutes-donnees` — Serveur MCP  - Accès unifié Parlement / Législation / Service Public ✺ Assemblée nationale & communauté
- [ ] `an-et-co-api-regroupement-toutes-donnees` — API - Accès unifié Parlement / Législation / Service Public ✺ Assemblée nationale & communauté
- [ ] `legiwatch-api-parlement` — API Parlement ✺ LegiWatch
- [ ] `legiwatch-database-parlement` — Base de données Parlement ✺ LegiWatch
- [ ] `legiwatch-serveur-mcp-parlement` — Serveur MCP Parlement ✺ LegiWatch

Aucune de ces ressources catalogue n'est directement intégrée : Parlementia
interroge l'API publique générique **data.gouv.fr** (recherche de jeux de
données par mot-clé, sans clé requise) pour son agent de recueil de données.

### Galerie
- [Image 1](images/TeamParlementia.jpg)
- [Image 2](images/image-2.png)

### Documents
- [Vidéo de démonstration — parcours utilisateur (~1 min 50)](hackathon-an-2026/docs/demo-parcours-utilisateur.mp4)
- [Tableur 1](hackathon-an-2026/docs/Classeur1.xlsx)
- [Document 2](hackathon-an-2026/docs/document-2.pdf)

### URL de démonstration
https://votre-application.example.com

### Diapositives de présentation
[Diapositives de présentation](docs/diapositives.pdf)
