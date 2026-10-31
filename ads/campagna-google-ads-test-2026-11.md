# Campagne Google Ads test, disdettaabbonamento.it (préparée le 31/10/2026)

Objectif : savoir en 14 jours si des Italiens paient 7,90 € pour l'envoi PEC. Pas de rentabilité attendue le premier mois.
Budget : 5 €/jour, arrêt automatique le 15/11 (date de fin de campagne). Coût max 70 €.

## Réglages du compte
- Nouveau compte Google Ads sur lardeuxlouis@gmail.com, pays de facturation France, devise EUR, fuseau Europe/Paris.
- Mode expert, « Créer une campagne sans objectif », type Réseau de Recherche, Réseau Display DÉCOCHÉ, partenaires de recherche décochés.
- Zone : Italie. Langue : italien. Appareils : tous.
- Enchères : Maximiser les clics, CPC max 0,35 €.
- Dates : 1/11 → 15/11/2026.
- URL finale par groupe = la fiche de la marque, suffixe de suivi : ?utm_source=google&utm_medium=cpc&utm_campaign=pec-test (le site reporte « google » dans le client_reference_id Stripe).

## Groupes d'annonces (1 marque = 1 groupe, mots clés en correspondance expression)
| Groupe | Mots clés (expression) | URL finale |
|---|---|---|
| Sky | "disdetta sky come fare", "disdetta sky pec", "inviare disdetta sky", "modulo disdetta sky", "disdetta sky online" | /disdetta-sky/ |
| DAZN | "disdetta dazn come fare", "disdetta dazn pec", "disdire dazn" | /disdetta-dazn/ |
| TIM | "disdetta tim pec", "disdetta linea tim come fare", "modulo disdetta tim" | /disdetta-tim/ |
| Vodafone | "disdetta vodafone pec", "disdetta vodafone come fare", "modulo disdetta vodafone" | /disdetta-vodafone/ |
| Fastweb | "disdetta fastweb pec", "disdetta fastweb come fare" | /disdetta-fastweb/ |
| McFit | "disdetta mcfit come fare", "disdetta mcfit pec", "modulo disdetta mcfit" | /disdetta-mcfit-italia/ |
| Generali | "disdetta polizza generali pec", "disdetta generali come fare" | /disdetta-generali-italia/ |
| Allianz | "disdetta allianz pec", "disdetta polizza allianz" | /disdetta-allianz-italia/ |
| Unipol | "disdetta unipol pec", "disdetta polizza unipol" | /disdetta-unipol/ |
| Verisure | "disdetta verisure come fare", "disdetta verisure pec" | /disdetta-verisure-italia/ |

Mots clés à exclure (campagne) : gratis, gratuito, lavoro, lavorare, numero verde, telefono, app, login, accedi, offerte, promozione, costo abbonamento, prezzo abbonamento, recensioni, stipendio.

## Annonce responsive (même modèle par groupe, {Marca} remplacé)
Titres (≤ 30 caractères) :
1. Disdetta {Marca} via PEC
2. Te la inviamo noi, 7,90 €
3. Ricevuta con valore legale
4. Indirizzo PEC verificato
5. Lettera pronta in 1 minuto
6. Senza PEC, senza posta
7. Disdetta {Marca} online
8. Vale come raccomandata A/R
Descriptions (≤ 90 caractères) :
1. Indirizzo PEC e preavviso di {Marca} verificati sulle fonti ufficiali. Lettera pronta, la inviamo noi.
2. Non serve avere una PEC né andare in posta: inviamo la disdetta e ti giriamo le ricevute via e-mail.
3. Lettera gratis da compilare, oppure invio PEC a 7,90 € con ricevuta di consegna entro 2 giorni lavorativi.
Chemin affiché : disdettaabbonamento.it/{marca}/pec

## Mesure
- Stripe : paiements dont le client_reference_id finit par « -google » = ventes venues de la pub.
- Google Ads : clics, CPC réel, taux de clic par groupe. On coupe un groupe sous 1 % de CTR après 100 impressions.
- Décision le 15/11 : coût par vente < 8 € → on continue et on monte le prix à 9,90 ; sinon on arrête et on garde le SEO.

## Révision du 31/10 midi, après lecture des données réelles (GSC 17 → 30/10)
Constat : 2 195 impressions, 30 clics, position 10,4. Montée très rapide (27/10 : 119 imp, 28/10 : 741, 29/10 : 1 333).
Ce qui remonte vraiment : **les assurances et les banques**, pas la télé ni le mobile. Sky, DAZN, TIM, Vodafone, Fastweb, McFit : zéro impression sur 14 jours (la page 1 y est tenue par les opérateurs eux mêmes et les gros comparateurs).
Pages les plus vues : Generali 101 imp, Unipol 89, Prima 79, Intesa Sanpaolo Protezione 77, BPER 74, Allianz 73, Cattolica 72, Allianz Direct 71, AXA 66, Orange Palestre 51, Verisure 46.
Requêtes : moitié « pec <marque> per disdetta » (l'adresse PEC), moitié « disdetta polizza <marque> ». Les gens cherchent déjà l'adresse PEC : ils ont donc l'intention d'envoyer une PEC, c'est exactement l'acheteur du service à 7,90 €. Un abonné Sky résilie en ligne, un assuré doit prouver sa disdetta avant l'échéance.

### Nouveaux groupes (remplacent le tableau du haut), 5 €/jour inchangé
| Groupe | Mots clés (expression) | URL finale |
|---|---|---|
| Polizza générique | "disdetta polizza via pec", "disdetta assicurazione pec", "inviare disdetta polizza", "lettera disdetta polizza", "disdetta polizza auto come fare" | / |
| Generali | "disdetta generali pec", "pec generali per disdetta", "disdetta polizza generali" | /disdetta-generali-italia/ |
| Allianz | "disdetta allianz pec", "pec allianz per disdetta", "disdetta polizza allianz", "disdetta allianz direct" | /disdetta-allianz-italia/ |
| Unipol | "disdetta unipol pec", "pec unipolsai disdetta", "disdetta polizza unipolsai" | /disdetta-unipol/ |
| AXA | "disdetta axa pec", "pec axa assicurazioni disdetta", "disdetta polizza axa" | /disdetta-axa-italia/ |
| Cattolica | "disdetta cattolica pec", "disdetta polizza cattolica" | /disdetta-cattolica-assicurazioni/ |
| Prima | "disdetta prima assicurazioni pec", "pec prima assicurazioni", "disdetta prima.it" | /disdetta-prima-assicurazioni/ |
| Verisure | "disdetta verisure pec", "recesso verisure", "come disdire verisure" | /disdetta-verisure-italia/ |
| Sky (témoin volume) | "disdetta sky pec", "inviare disdetta sky", "modulo disdetta sky" | /disdetta-sky/ |

Mots exclus en plus : sinistro, preventivo, rinnovo, pagare, pagamento, area clienti, numero, telefono, lavora con noi.

### Annonce pour les groupes assurance (remplace {Marca})
Titres : Disdetta {Marca} via PEC · Te la inviamo noi, 7,90 € · Ricevuta con valore legale · Prima della scadenza · Indirizzo PEC verificato · Lettera pronta in 1 minuto · Senza PEC, senza posta · Vale come raccomandata A/R
Descriptions : Indirizzo PEC e preavviso di {Marca} verificati sulle fonti ufficiali. Lettera pronta, la inviamo noi. · Non serve avere una PEC né andare in posta: inviamo la disdetta e ti giriamo le ricevute via e-mail. · Lettera gratis da compilare, oppure invio PEC a 7,90 € con ricevuta di consegna entro 2 giorni lavorativi.

### Ce que ça change pour la lecture du test
Le trafic naturel sur ces mêmes pages grossit de lui même (x10 en 3 jours). Pour ne pas attribuer au SEO ce que la pub apporte, la seule mesure qui compte reste le suffixe « -google » dans Stripe, et le rapport termes de recherche de Google Ads au bout de 7 jours.
