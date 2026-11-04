---
title: "NG-Stego — Phase I (A1–A3) : bilan scientifique et audit"
subtitle: "DSP-D-26-02810 | Dossier de recherche distinct du manuscrit Version 1.0"
date: "4 novembre 2026"
lang: fr-FR
---

# Décision scientifique

**La Phase I a permis d'établir un résultat variationnel sous hypothèses précises et d'obtenir une décomposition du surcoût géométrique vérifiée sur deux modèles. Elle n'établit pas encore une nouveauté mathématique générale ni un bénéfice stéganographique opérationnel.** L'étape A1 révèle des antériorités particulièrement pertinentes qui doivent être reconnues avant toute intégration au manuscrit.

Nous conservons la **Version 1.0** de l'article, de la réponse aux évaluateurs et de la lettre comme référence inchangée. Les éléments qui suivent sont un dossier scientifique exploratoire audité, avec sources, tests et fichiers numériques séparés.

# A1 — Antériorités et frontières exactes des contributions

| Publication vérifiée | Résultat déjà établi | Conséquence pour NG-Stego |
|---|---|---|
| **Papangelou (2000)**, Annals of Applied Probability, DOI [10.1214/aoap/1019487616](https://doi.org/10.1214/aoap/1019487616) | Principe de grandes déviations pour Wright–Fisher, action Fisher, minimiseur géodésique et concentration conditionnelle des trajectoires | Le principe variationnel et l'interprétation probabiliste dans ce modèle ne sont pas nouveaux. |
| **Pavlichin–Weissman (2016)**, IEEE ISIT, DOI [10.1109/ISIT.2016.7541365](https://doi.org/10.1109/ISIT.2016.7541365) | Minimisation des KL chaînées sur le simplexe fini, chemins optimaux à temps discret et limite continue | La minimisation discrète non contrainte et sa limite ne constituent pas notre nouveauté. |
| **Rumpf–Wirth (2015)**, IMA J. Numer. Anal., DOI [10.1093/imanum/dru027](https://doi.org/10.1093/imanum/dru027) | Discrétisation variationnelle du calcul géodésique sur des variétés ; convergence fondée sur la Γ-convergence | Le passage général « énergie discrète → géodésique continue » possède déjà un cadre abstrait éprouvé. |
| **Maas et al. (2015)**, ESAIM:M2AN, DOI [10.1051/m2an/2015043](https://doi.org/10.1051/m2an/2015043) | Minimisation de sommes de coûts successifs entre images et géodésiques discrètes dans une autre géométrie | Le principe d'optimisation de chemins d'images par étapes est antérieur. |
| **Nielsen (2024)**, Handbook of Statistics, DOI [10.1016/bs.host.2024.06.003](https://doi.org/10.1016/bs.host.2024.06.003) | Techniques d'approximation et de bornage des distances Fisher–Rao des modèles paramétriques ; plongements de sous-variétés | Les bornes d'immersion dans l'espace ambiant sont des outils déjà disponibles. |

**Portée de cette recherche :** matrice ciblée des sources identifiées ; elle ne prétend pas être une revue systématique exhaustive. Le PDF de Papangelou transmis est une publication scientifique complète ; celui de Pavlichin–Weissman est une version auteur de l'article de 2016. Les formules ont été confrontées aux passages correspondants de ces documents.

## Positionnement rigoureux

La relation initiale du Théorème 3(iv), pour un chemin prescrit, relève de l'expansion locale de KL et d'une somme de Riemann. Les travaux de Papangelou et Pavlichin–Weissman comportent des résultats variationnels plus forts mais dans un modèle probabiliste et/ou un simplexe spécifiques. Nous ne devons **ni attribuer le Théorème 3(iv) à ces auteurs comme s'ils l'avaient énoncé dans toute sa généralité, ni présenter la minimisation géodésique générale comme une découverte nouvelle.**

# A2 — Théorème variationnel effectivement démontré

## Hypothèses

La famille de distributions représentables par le générateur est supposée être une **sous-variété compacte, connexe, identifiable, de classe C³, plongée sans bord dans l'intérieur d'un simplexe fini**. La métrique est la métrique de Fisher–Rao induite ; elle est non dégénérée en coordonnées intrinsèques.

Ce modèle théorique couvre des familles finies régulières. Il **ne garantit pas automatiquement** le cas du VAE ReLU original : la régularité globale, l'identifiabilité et l'absence de singularité n'y sont pas établies.

## Résultat

Nous définissons, avec deux distributions admissibles fixées $a,b$,

$$
C_N^G(a,b)=\min_{P_1,\ldots,P_{N-1}\in\mathcal M_G}
\sum_{j=0}^{N-1}D_{\mathrm{KL}}(P_{j+1}\|P_j).
$$

Sous les hypothèses ci-dessus, le calcul variationnel donne :

$$
\boxed{\lim_{N\to\infty}N C_N^G(a,b)=\frac12d_G(a,b)^2.}
$$

Les minima discrets existent. L'interpolation des chaînes minimisantes possède des sous-suites convergeant uniformément vers des géodésiques intrinsèques minimisantes à vitesse constante. Si celle-ci est unique, la convergence concerne la suite entière.

Une borne de convergence prudente sur les valeurs est obtenue :

$$
\frac12d_G^2-O(N^{-1/2})\le N C_N^G\le\frac12d_G^2+O(N^{-1}).
$$

Le raisonnement exploite : un chemin géodésique témoin pour la borne supérieure ; la coercivité locale uniforme de KL sur la variété compacte ; l'inégalité de Cauchy–Schwarz ; puis la compacité des interpolations et la semi-continuité inférieure de l'énergie pour les trajectoires minimisantes.

**Portée scientifique :** cette démonstration spécialisée est présentée dans la note mathématique anglaise jointe. Elle n'est pas encore certifiée par une évaluation mathématique indépendante, et les techniques de discrétisation variationnelle ont des antériorités substantielles. Le résultat ne prouve pas que l'Algorithme 2 atteint le minimum discret.

# A3 — Trois coûts géométriques distincts

Pour une trajectoire admissible $\gamma$ :

$$
\begin{aligned}
E_F[\gamma]-d_{\mathrm{amb}}^2
={}&(E_F[\gamma]-\ell_F[\gamma]^2)\\
&+(\ell_F[\gamma]^2-d_G^2)\\
&+(d_G^2-d_{\mathrm{amb}}^2).
\end{aligned}
$$

Les termes expriment le coût de paramétrisation, le détour du chemin admissible et la restriction imposée par le générateur. **C'est une identité géométrique classique ; sa nouveauté éventuelle résidera dans un diagnostic quantitatif propre à NG-Stego, puis dans son utilité démontrée.**

## Validation exactement calculable : anneau Bernoulli

Une famille à deux variables Bernoulli indépendantes est définie par $p_1(u)=0,5+0,22\cos u$ et $p_2(u)=0,5+0,23\sin u$, avec $u$ périodique. Elle forme une sous-variété lisse, compacte, identifiable et régulière de l'intérieur du simplexe à quatre issues.

| Mesure exacte ou haute précision | Valeur |
|---|---:|
| Distance Fisher–Rao ambiante $d_{\mathrm{amb}}$ | 0,903486 |
| Distance intrinsèque $d_G$ | 1,385839 |
| Surcoût propre au générateur $d_G^2-d_{\mathrm{amb}}^2$ | **1,104264** |
| Limite visée $d_G^2/2$ | 0,960275 |
| Coût $N\sum \mathrm{KL}$ du chemin témoin à $N=256$ | **0,960260** |

Attention : la dernière valeur provient d'une **chaîne admissible échantillonnant une géodésique intrinsèque**. Il ne s'agit pas d'une certification du minimum discret global à $N=256$. La convergence théorique des minima est obtenue séparément par le théorème.

Pour un chemin long parcouru à vitesse variable, l'identité à trois termes donne respectivement **0,785560** (vitesse), **0,391334** (trajet) et **1,104264** (générateur), avec résidu numérique inférieur à $10^{-14}$.

![Approche de l'énergie Fisher par la somme des KL sur le modèle analytique](figures/toy_variational_limit.png){ width=55% }

## VAE Bernoulli réel : bornes et non certification globale

Nous avons repris le checkpoint VAE existant, vérifié son empreinte SHA-256 et calculé le coefficient de Bhattacharyya des 784 pixels Bernoulli sans énumérer les $2^{784}$ images possibles.

Le décodage des logits et de la métrique utilise les poids réels. Les lignes latentes sont scindées exactement aux frontières d'activation ReLU identifiables ; chaque sous-segment lisse est intégré par quadrature de Gauss–Legendre. Les polylignes optimisées ne sont que des candidats admissibles.

| Paire | Borne inférieure ambiante exacte | Longueur d'un chemin admissible (estimation) | Encadrement du surcoût modèle² (estimé) |
|---|---:|---:|---:|
| Local, sans frontière ReLU | 0,786793 | 0,797413 | [0 ; 0,016824] |
| Local, 2 frontières | 1,143427 | 1,180495 | [0 ; 0,086143] |
| Autre paire, 2 frontières | 1,071958 | 1,101029 | [0 ; 0,063171] |
| Séparation modérée, 17 frontières | 2,999096 | 5,409763 | [0 ; 20,270959] |

La distance intrinsèque réelle du VAE n'est **pas calculée exactement**. La borne basse ambiante est rigoureuse pour les distributions considérées. La borne haute est une longueur de chemin admissible **évaluée numériquement**, dont l'incertitude de quadrature n'a pas été certifiée par arithmétique d'intervalles. Ces intervalles ne doivent donc pas être qualifiés de bornes numériques formellement certifiées.

![Comparaison des bornes inférieures et des chemins admissibles pour le VAE](figures/vae_length_bounds.png){ width=55% }

# Audit technique

- Script numérique exécuté à partir des poids et de la structure du décodeur VAE conservés dans l'archive du projet.
- **9 tests unitaires réussis**, dont KL versus Fisher par développement local et quadratures à deux ordres distincts.
- Les calculs utilisent des semences et des paramètres de test fixes. Les graphiques et résultats JSON/CSV sont régénérés par un seul script.
- La preuve sur variété compacte et l'expérimentation ReLU sont volontairement distinguées.
- Les contraintes de détectabilité, charge utile et décodage opérationnel ne sont pas encore évaluées dans cette phase ; aucune revendication de supériorité de NG-Stego n'en découle.

# Décision : passerelle vers la Phase II

**A1 :** matrice d'antériorité ciblée réalisée ; compléter la revue avant toute revendication de nouveauté. **A2 :** theorem avec démonstration et limites explicites obtenu ; à soumettre à une revue contradictoire. **A3 :** identité exacte, validation analytique et premiers diagnostics VAE exécutés ; estimation précise de la distance intrinsèque VAE encore ouverte.

Pour que ce développement devienne une contribution publiable plutôt qu'un résultat géométrique illustratif, la prochaine étape doit : (i) obtenir des intervalles plus serrés et indépendamment vérifiés sur $d_G$, (ii) relier ces mesures à l'Algorithme 2 réel, (iii) évaluer sur codebooks tenus à l'écart si elles prédisent les échecs de convergence ou de décodage **au-delà** des métriques usuelles, et (iv) traiter les frontières ReLU ainsi que le modèle de menace.

La Version 1.0 de l'article, sa réponse et sa lettre restent **inchangées**. La synchronisation GitHub concerne les éléments de recherche auditables, sans réécrire les revendications du manuscrit.
