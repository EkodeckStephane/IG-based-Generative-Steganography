# DSP-D-26-02810 — Audit experimental de la frontiere multiobjectif de NG-Stego (Algorithme 2)
**Date : 31 octobre 2026.** Campagne reproductible sur le VAE Bernoulli-MNIST du manuscrit. **Verdict : la revendication d'une superiorite operationnelle de Fisher-Rao n'est pas etablie.** Il ne faut pas convertir ces resultats en resultats positifs dans la revision officielle.

## 1. Question et protocole fige

Comparer une instanciation numerique directe de l'Algorithme 2 (gradient de la divergence Bernoulli, matrice de Fisher estimee par scores Monte-Carlo, pas de second algorithme) aux gradients exact-Fisher et euclidien. Tous les optimiseurs utilisent la meme fonction objectif KL(P_z || P_target), le meme VAE, les memes points de depart, six codebooks tires independamment, un message uniforme a deux bits par image et un detecteur RBF-SVM au meme parametrage. Les sauvegardes de l'algorithme ajoutent regularisation de la FIM, recherche de pas d'Armijo, tolerance et nombre maximal d'iterations : ce sont des garde-fous numeriques **absents de la pseudocode source**, donc cette campagne constitue une *instanciation fidele de la regle de mise a jour*, non une execution litterale de chaque detail du pseudo-code.

Le point de depart cover est z0=(0,0), les 24 mots de code sont distincts de z0 et separes. Les codebooks 0-2 alimentent l'apprentissage du detecteur; les codebooks 3-5 sont reserves au test sans re-entrainement. Chaque codebook de test comprend 100 covers et 100 stegos par methode, soit 300 messages test par methode. Les echantillonnages et les messages de test utilisent des graines fixes, des matrices de nombres aleatoires appariees et les memes conditions entre optimiseurs. Les AUC sont calculees par codebook puis moyennees; elles ne forment pas une mesure de securite universelle.

Les quatre dimensions de Pareto sont (1) erreur du **decodeur VAE public** (minimiser), (2) avantage du meilleur des trois detecteurs observes, dont un oracle connaissant le modele (minimiser), (3) MSE entre probabilites du decodeur et du cover (minimiser), (4) temps d'optimisation par mot de code (minimiser). Le temps de pre-calcul du codebook ne doit PAS etre confondu avec l'encodage par image. Les certificats de variation totale issus de Pinsker sont non informatifs (bornes proches de 1) pour la plupart des trajectoires.

## 2. Tableau principal : performance sur les codebooks de test

| Methode | Decodage public | AUC pixels | AUC latent public | AUC oracle | KL moyen cover (nats) | MSE probabilites |
|---|---:|---:|---:|---:|---:|---:|
| NoShift_T0 | 23.3% | 0.530 | 0.521 | 0.500 | 0.00 | 0.0000 |
| FisherMC_N256_T1 | 51.3% | 0.906 | 0.945 | 0.998 | 31.51 | 0.0137 |
| FisherMC_N256_T3 | 65.7% | 0.988 | 0.988 | 0.999 | 62.28 | 0.0252 |
| FisherMC_N256_T10 | 85.0% | 0.987 | 0.988 | 0.999 | 79.54 | 0.0301 |
| FisherMC_N256_T80 | 85.0% | 0.987 | 0.988 | 0.999 | 79.54 | 0.0301 |
| Euclidean_T3 | 85.7% | 0.993 | 0.998 | 1.000 | 92.62 | 0.0340 |
| Euclidean_T10 | 95.0% | 0.993 | 0.999 | 1.000 | 83.68 | 0.0320 |
| Euclidean_T80 | 95.0% | 0.993 | 0.998 | 1.000 | 83.78 | 0.0320 |

Ces performances sont mesurees pour **une charge utile nominale de deux bits par image**; les echecs de decodage empechent d'interpreter ce debit comme une capacite operationnelle fiable. Le controle negatif NoShift donne environ 23,3% de decodage public, coherent avec une tentative de lire un message non incorpore.

## 3. References adaptees, meme canal, mais decodeurs differents

| Reference | Decodage par son propre decodeur | AUC SVM pixels | AUC SVM latent | Encodage median/image |
|---|---:|---:|---:|---:|
| iMEC adapte | 300/300 | 0.507 | 0.513 | 30.72 ms |
| Discop adapte | 300/300 | 0.508 | 0.532 | 1.59 ms |

Les baselines iMEC et Discop emploient leurs decodages propres et leurs adaptateurs au canal Bernoulli; elles ne sont PAS les pipelines natifs complets (texte/images) de leurs articles d'origine. La comparaison de temps n'est pas directe : NG-Stego exige un pre-calcul des parametres du codebook, tandis que le temps baseline porte sur l'encodage en ligne. La distorsion des baselines est estimee dans le domaine empirique des proportions de pixels, alors que la colonne MSE du chemin correspond a une differente quantite theorique. Elles ne doivent PAS etre confondues dans la meme frontiere quantitative.

## 4. Analyse et deduction de portee scientifique

- Sur les trois codebooks de test, l'Algorithme 2 avec Fisher Monte-Carlo N=256 et T=10 atteint **255/300 (85%)** de decodage public; la descente euclidienne T=10 atteint **285/300 (95%)**. La difference est descriptive et reste limitee a seulement trois codebooks.
- Les detecteurs entraines sur d'autres codebooks et l'oracle distribue presentent des AUC elevees pour les mecanismes d'optimisation, meme aux premiers pas. L'Algorithme 2 n'obtient pas un point combinant fiabilite elevee et faible detectabilite dans les configurations evaluees.
- Le gradient naturel a un sens geometrique : il preconditionne la trajectoire, sans changer la fonction objectif finale. Pour des cibles identiques, si les deux methodes convergent au meme P_target, la distribution finale et sa detectabilite endpoint sont identiques. Sans nouvelle contrainte de securite ou avantage sur le chemin *observable*, la theorie ne peut promettre une meilleure securite endpoint de Fisher.
- La frontiere de Pareto contient des solutions de faibles taux d'erreur et d'autres plus economes en divergence; elle ne contient pas de solution attestant une **dominance simultanee** de Fisher sur Euclide et les adaptateurs iMEC/Discop.

## 5. Risques et modifications de la soumission

**R2.3 demeure partiel :** nous avons un adversaire RBF sur pixels et latents observables, un oracle blanc-connaissant-les-distributions, et un split codebook independant; pas de validation robuste par d'autres detecteurs CNN au sein de cette nouvelle campagne, ni garantie de securite adversariale, ni entrainement adversarial robuste de l'Algorithme 2. L'adversaire oracle est informatif mais ne modelise pas necessairement un adversaire ne connaissant pas la cle secrete.

**R2.7 demeure partiel :** cinq variantes d'optimisation, deux baselines au meme canal, charges et echantillons apparis, mais le mecanisme original S5 en moyennes de classes MNIST et les pipelines iMEC/Discop natifs complets ne sont pas reproduits par cette campagne; comparabilite des decodeurs et des temps limitee. Distorsion perceptuelle (LPIPS/FID), image naturelle et second generateur non evalues.

**Recommandation pre-soumission :** conserver le positionnement de l'article sur le cadre d'analyse mathematique des trajectoires Fisher-Rao; ne pas affirmer une superiorite operationnelle de NG-Stego. La reponse au reviewer peut annoncer la nouvelle comparaison negative et ses hypotheses exactes, mais ne peut pas pretendre avoir satisfait integralement R2.3/R2.7. Une optimisation multiobjectif explicitement contrainte par la divergence cover sera une methode **nouvelle**, a presenter comme extension distincte et non comme preuve retroactive de l'Algorithme 2.

## 6. Audit et reproduction

Fichiers : `pareto_algorithm2_v1.py`, `evaluate_common_channel_baselines.py`, `test_pareto_algorithm2_v1.py`, les JSON detailles, CSV, logs, figures et dependances echantillon. Controle independant du gradient de KL, semidefinite-positivite de F, controle de decroissance du KL, integrite des graines, partition codebook et verification automatique du Pareto : **PASS**. Empreinte SHA-256 du checkpoint : `e94d57b36d960921768ce8ccc889796d5cd4ce69ce794a90ed1b669ed1d1ed61`.

*Attention:* cette campagne est exploratoire; 300 messages n'impliquent pas 300 modeles independants, les intervalles bootstrap sont conditionnels aux codebooks et a ce generateur. Les temps sont des mesures CPU et peuvent varier selon la machine. Tout jugement d'acceptation demeure du ressort des reviewers et de l'editeur.