#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fingerprint_check.py — Vérificateur d'empreinte d'écriture (français).
Scanne le texte contre 24 formulations "robot" interdites, vérifie les
négations complètes trop systématiques, les accents manquants, l'excès de
questions rhétoriques et les conclusions formelles.
Score 0-100, minimum 55 pour passer. Suggère 2-3 tics verbaux naturels.

Usage :
    python3 fingerprint_check.py fichier.md
    echo "texte" | python3 fingerprint_check.py
"""
import random
import re
import sys

SEUIL = 55

# 24 formulations robot interdites (corporate / IA générique)
FORMULATIONS_ROBOT = [
    r"dans un monde où",
    r"il est important de noter",
    r"il convient de",
    r"il est essentiel de",
    r"n'hésitez pas à",
    r"que vous soyez .{3,40} ou",
    r"plongeons(?:-nous)? dans",
    r"explorons ensemble",
    r"en tant que .{3,30}, (?:vous|il|elle)",
    r"à l'ère du numérique",
    r"dans le paysage actuel",
    r"r[ôo]le crucial",
    r"un véritable game[- ]?changer",
    r"révolutionn(?:er|aire)",
    r"libérez (?:votre|le) potentiel",
    r"passer au niveau supérieur",
    r"sans plus attendre",
    r"cerise sur le gâteau",
    r"force est de constater",
    r"il va sans dire",
    r"vous l'aurez compris",
    r"alors, qu'attendez-vous",
    r"en un mot comme en cent",
    r"le maître[- ]mot",
]

CONCLUSIONS_FORMELLES = [
    r"\ben conclusion\b", r"\bpour conclure\b", r"\ben somme\b", r"\ben définitive\b",
    r"\bpour résumer\b", r"\ben résumé\b", r"\bau terme de\b",
]

# Mots fréquents dont l'absence d'accent trahit un texte bâclé
ACCENTS = {
    "etre": "être", "tres": "très", "deja": "déjà", "voila": "voilà",
    "apres": "après", "meme": "même", "plutot": "plutôt", "gout": "goût",
    "interet": "intérêt", "role": "rôle", "cote": "côté", "ca": "ça",
    "francais": "français", "prefere": "préfère", "reussite": "réussite",
}

TICS_NATURELS = [
    "franchement", "bref", "du coup", "au final", "honnêtement",
    "bon,", "en vrai", "spoiler :", "petit détail :", "d'ailleurs",
]


def analyser(texte):
    problemes = []
    penalites = 0
    texte_bas = texte.lower()

    # --- 1. Formulations robot (jusqu'à -60)
    robots = []
    for pattern in FORMULATIONS_ROBOT:
        m = re.search(pattern, texte_bas)
        if m:
            robots.append(m.group(0))
    if robots:
        penalites += min(60, 15 * len(robots))
        problemes.append(
            f"Formulations corporate détectées ({len(robots)}) : "
            + " | ".join(f"« {r} »" for r in robots[:5])
            + " → à réécrire avec vos propres mots (bloquant)."
        )

    # --- 2. Négations : "ne ... pas" systématique = registre trop formel
    phrases = [p.strip() for p in re.split(r"[.!?\n]+", texte) if p.strip()]
    neg_completes = len(re.findall(r"\bne\s+\w+\s+(?:pas|plus|jamais|rien)\b", texte_bas))
    neg_incompletes = len(re.findall(r"\b(?:c'est|y a|faut|j'ai|on)\s+(?:pas|plus|jamais|rien)\b", texte_bas))
    total_neg = neg_completes + neg_incompletes
    if total_neg >= 3 and neg_incompletes == 0:
        penalites += 10
        problemes.append(
            f"Négations 100% complètes ({neg_completes}) : registre trop formel. "
            f"→ Glisser 1-2 négations orales (« c'est pas », « y a pas »)."
        )

    # --- 3. Accents manquants (jusqu'à -20)
    manquants = []
    for sans, avec in ACCENTS.items():
        if re.search(rf"\b{sans}\b", texte) and sans != "ca":
            manquants.append(f"{sans} → {avec}")
        elif sans == "ca" and re.search(r"(?<![çc])\bca\b", texte):
            manquants.append("ca → ça")
    if manquants:
        penalites += min(20, 5 * len(manquants))
        problemes.append("Accents manquants : " + ", ".join(manquants[:6]))

    # --- 4. Questions rhétoriques (max 1 pour 8 phrases)
    questions = len(re.findall(r"\?", texte))
    if phrases and questions > max(1, len(phrases) // 8):
        penalites += 10
        problemes.append(
            f"{questions} questions rhétoriques pour {len(phrases)} phrases : "
            f"tic d'écriture IA. → En garder 1 maximum, transformer le reste en affirmations."
        )

    # --- 5. Conclusions formelles (-15)
    for pattern in CONCLUSIONS_FORMELLES:
        if re.search(pattern, texte_bas, re.MULTILINE):
            penalites += 15
            problemes.append(
                "Conclusion formelle détectée (« en conclusion »-style). "
                "→ Finir sur une phrase concrète, un chiffre ou un conseil direct."
            )
            break

    # --- 6. Présence de tics naturels (bonus déjà présent, sinon suggestion)
    tics_presents = [t for t in TICS_NATURELS if t.rstrip(",: ") in texte_bas]
    if len(tics_presents) < 2:
        penalites += 10
        suggestions = random.sample([t for t in TICS_NATURELS if t not in tics_presents], 3)
        problemes.append(
            f"Seulement {len(tics_presents)} tic(s) verbal(aux) naturel(s). "
            f"→ En insérer 2-3, par exemple : {', '.join('« ' + s + ' »' for s in suggestions)}."
        )

    score = max(0, 100 - penalites)
    return score, problemes, robots


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            texte = f.read()
    else:
        texte = sys.stdin.read()

    if not texte.strip():
        print("Texte vide — rien à vérifier.")
        sys.exit(1)

    score, problemes, robots = analyser(texte)

    print("=" * 52)
    print("FINGERPRINT CHECK (empreinte d'écriture)")
    print("=" * 52)
    print(f"  SCORE : {score}/100   (minimum : {SEUIL})")
    print("=" * 52)

    if problemes:
        print("\nÀ corriger :")
        for i, p in enumerate(problemes, 1):
            print(f"  {i}. {p}")

    if robots:
        print(f"\n❌ BLOQUÉ : {len(robots)} formulation(s) corporate — correction obligatoire.")
        sys.exit(1)
    if score < SEUIL:
        print(f"\n❌ BLOQUÉ (score {score} < {SEUIL})")
        sys.exit(1)
    print("\n✅ Empreinte validée — le texte sonne humain.")
    sys.exit(0)


if __name__ == "__main__":
    main()
