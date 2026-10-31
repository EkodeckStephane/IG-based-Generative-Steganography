# DSP-D-26-02810 — Reviewer 2, R2.3 et R2.7 : audit expérimental approfondi
**Date :** 31 octobre 2026 · **Statut :** résultats expérimentaux vérifiés, **satisfaction intégrale non démontrée**.

## Synthèse

Le renforcement expérimental a atteint trois objectifs vérifiables : (i) comparer réellement l'optimiseur de type Algorithme 2 à ses ablations et à des adaptateurs iMEC/Discop sur un canal Bernoulli-VAE commun ; (ii) évaluer des détecteurs informés sur plusieurs codebooks indépendants, sans que le codeword cover soit un message ; (iii) entraîner **une variante adversariale** du codebook, puis évaluer une stéganalyse indépendante et un test de vraisemblance utilisant le modèle public. L'amélioration de l'indétectabilité **dégrade la fiabilité du décodage**. Ni l'Algorithme 2 original ni la nouvelle variante ne démontrent de supériorité opérationnelle générale. Ne pas présenter cette étude comme une levée définitive de R2.3/R2.7.

### R2.7 — Rappel de la campagne multicodes antérieure

Protocole : un VAE MNIST-Bernoulli de dimension latente 2, quatre codebooks indépendants, quatre messages à 2 bits, aucun codeword égal à z0 ; 80 covers et 80 stegos par codebook dans chaque ensemble d'évaluation. Détecteur SVM-RBF entraîné sur 3 codebooks et évalué sur le quatrième. Les méthodes iMEC et Discop sont des **adaptations au canal**, et non leurs pipelines natifs image.

| Méthode | Cibles convergentes | Décodage ML/natif | Décodage via encodeur public | AUC SVM image moyenne |
|---|---:|---:|---:|---:|
| Algorithme 2, Fisher Monte Carlo | 8/16 | 318/320 | 198/320 | 0,9519 |
| Fisher exacte | 8/16 | 318/320 | 202/320 | 0,9535 |
| Gradient euclidien | 12/16 | 319/320 | 260/320 | 0,9781 |
| iMEC, adaptation Bernoulli | — | 320/320 | n/a | 0,5013 |
| Discop, adaptation Bernoulli | — | 320/320 | n/a | 0,4926 |

Source : `Version_1.0/research_evidence/multicodebook_results.json` avec graines, solutions latentes et évaluations détaillées. Ces décodages ML/natifs ne mesurent **pas la même connaissance du récepteur**. Les AUC iMEC/Discop sur « codebook non vu » correspondent à des splits de données, leurs algorithmes ne dépendant pas du codebook.

### R2.3 — Entraînement adversarial : variante nouvelle, et non Algorithme 2 original

Le décodeur Bernoulli-VAE est fixé. Quatre paramètres latents sont entraînés contre un discriminant image à deux couches, avec échantillonnage Bernoulli à gradient **straight-through biaisé** et perte auxiliaire de décodage par vraisemblance. Le détecteur entraîné lors de l'optimisation n'est **jamais** réutilisé dans l'évaluation finale. La nouvelle stéganalyse contient un SVM-RBF sur pixels, un SVM-RBF sur représentation fournie par l'encodeur VAE public, et un oracle de rapport de vraisemblance pour le codebook connu. Trois répétitions à graines indépendantes, chacune avec 400 covers+400 stegos pour l'entraînement des SVM et 800+800 exemples de test. Au total, 2 400 messages de test par variante. Les 4 configurations ci-dessous utilisent **un seul codebook initial** ; il ne s'agit pas d'une preuve de généralisation.

| Variante (poids adversarial) | AUC pixels SVM | AUC latent SVM | AUC oracle | ML correct | Encodeur VAE correct |
|---|---:|---:|---:|---:|---:|
| Initiale, non entraînée | 0,832 | 0,931 | 0,990 | 2369/2400 (98,7 %) | 2029/2400 (84,5 %) |
| 0 (contrôle décodage) | 0,960 | 0,979 | 0,998 | 2400/2400 (100 %) | 2390/2400 (99,6 %) |
| 1 | 0,539 | 0,645 | 0,789 | 1933/2400 (80,5 %) | 1397/2400 (58,2 %) |
| 3 | 0,523 | 0,559 | 0,638 | 1193/2400 (49,7 %) | 910/2400 (37,9 %) |

**Interprétation :** le simple rapprochement de l'AUC image vers 0,5 ne suffit pas. Le détecteur latent/encodeur reste efficace, l'oracle plus encore, et le décodage se détériore. Le poids 3 aboutit à des codewords presque confondus (séparation minimale ≈ 0,013), ce qui rend le résultat faible AUC non intéressant comme stéganographie fiable. Les AUC sont des moyennes descriptives de trois tests ; elles ne constituent pas des intervalles de confiance sur de nouveaux générateurs.

### Test optimal et compromis charge utile/détectabilité

Un test de Neyman–Pearson sous hypothèses simples a été évalué par le rapport de vraisemblance **exactement calculable** sur les 784 sorties Bernoulli, pour le mélange uniforme des quatre distributions message. C'est un **oracle white-box**, non un détecteur déployable sans hypothèses. Sur un cercle de quatre codewords à distance latente fixée du cover, **et en supposant les cibles parfaitement atteintes**, on trouve :

| Rayon | AUC oracle | Réussite ML |
|---:|---:|---:|
| 0,02 | 0,536 | 37,6 % |
| 0,05 | 0,652 | 56,2 % |
| 0,10 | 0,838 | 81,2 % |
| 0,20 | 0,990 | 98,6 % |
| 0,40 | ≈ 1,000 | 100 % |

Évaluation : 2 500 covers + 2 500 stegos par rayon ; une seule géométrie de codebook et un seul générateur. Ces valeurs illustrent un **compromis empirique**, non un théorème universel.

### R2.7 — Distorsion, temps, comparabilité

Sur R1, 200 messages de 2 bits par méthode, CPU, codebook précalculé pour les optimisateurs :

| Méthode | Pré-calcul du codebook | Encodage médian | Décodage médian | MSE vers la moyenne cover |
|---|---:|---:|---:|---:|
| Algorithme 2 MC Fisher | 532 ms | 0,0155 ms | 0,0069 ms | 0,0931 |
| Fisher exacte | 620 ms | 0,0156 ms | 0,0067 ms | 0,0931 |
| Gradient euclidien | 461 ms | 0,0159 ms | 0,0069 ms | 0,1013 |
| iMEC Python canal commun | — | 58,77 ms | 41,97 ms | 0,0654 |
| Discop Python canal commun | — | 2,46 ms | 2,43 ms | 0,0648 |

**Avertissements majeurs :** (1) Le pré-calcul des quatre cibles est une charge *offline* et n'est pas inclus dans l'encodage en ligne. (2) Le décodeur des trajectoires utilise des distributions de sortie connues (oracle ML), pas le VAE public ; les temps ne sont pas homogènes quant à la connaissance et au travail requis. (3) Le Python public d'iMEC n'est pas son C++ optimisé ; Discop utilise ici un port Python, pas son backend Cython. (4) La MSE est relative à l'**image d'espérance de la distribution cover**, ce n'est ni une distorsion cover-stego appariée ni un indicateur perceptuel.

## Décision scientifique

**R2.3 : renforcé, mais pas intégralement satisfait.** Il existe désormais une expérience de co-entraînement adversarial **sur un nouveau codebook**, et une évaluation indépendante plus exigeante ; mais l'entraînement ne porte pas sur l'Algorithme 2 tel que décrit dans le papier, ne démontre aucune robustesse à un adversaire white-box, et n'a été étudié que pour une seule initialisation et un seul VAE.

**R2.7 : renforcé, mais pas intégralement satisfait.** Le protocole canal commun, la séparation offline/online, la capacité de récupération, la détectabilité et la MSE-proxy sont documentés. Des comparaisons natives aux modèles images iMEC/Discop en conditions réellement équivalentes, une réévaluation sur les données MNIST brutes d'origine et des protocoles à qualité perceptuelle/capacité *appariées* restent indisponibles. Les expériences natives texte réalisées antérieurement ne remplacent pas une comparaison image-image.

**L'article, la réponse au reviewer et la cover letter officiels ne sont pas modifiés par cette campagne.** Toute future intégration devra présenter les résultats défavorables, les décodeurs distincts et la différence entre Algorithme 2 et sa variante adversariale. Sans cela, la réponse au reviewer serait trompeuse.

## Reproductibilité et audit

Le ZIP joint comprend le checkpoint VAE, `benchmark_s5_comparison.py`, les références iMEC nécessaires au canal, tous les scripts, les JSON, les CSV, les journaux et le test d'intégrité. Depuis le dossier racine du paquet :

```bash
export DSP_PROJECT_ROOT="$PWD"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python Version_1.0/research_evidence/test_adversarial_research_package.py
python Version_1.0/research_evidence/oracle_detection_tradeoff.py
python Version_1.0/research_evidence/minimax_codebook_prototype.py
python Version_1.0/research_evidence/adaptive_detector_independent_eval_v2.py
python Version_1.0/research_evidence/iso_channel_runtime_audit.py
```

Prérequis : Python, NumPy, SciPy, scikit-learn, PyTorch. Les résultats sont figés par empreintes dans `MANIFEST_SHA256.json`. Les essais indépendants ont été calculés sur CPU, avec des graines documentées. Les calculs Monte-Carlo sont soumis aux aléas et aux versions de bibliothèques ; une proximité statistique, plutôt qu'une égalité octet à octet, est attendue pour certaines opérations.