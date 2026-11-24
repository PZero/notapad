---
description: Chiusura veloce, solo documenti locali (niente pagina, README, commit né push)
model: sonnet
---

Chiusura veloce della sessione. Niente sottoagenti, niente rigenerazioni, niente test. Senza rileggere file che non servono:

1. Aggiorna `docs/STATO.md`: data di oggi, fase attuale, cosa è stato fatto in questa sessione, cosa è in corso, prossimi passi, cosa è in pausa. **Riscrivi** il file tenendolo sotto le 60 righe: è una fotografia dello stato, non un diario. In fondo annota: «Ultima chiusura veloce: <data>, documenti non pubblicati (pagina, README, CHANGELOG e commit al prossimo `/fine-sessione`).»
2. Aggiungi a `docs/DECISIONI.md` le decisioni prese oggi (una riga nella tabella: data, decisione, motivazione). Non riscrivere quelle vecchie. Aggiorna `docs/DOMANDE-APERTE.md` solo se qualcosa è cambiato.
3. Se sono cambiati componenti o pin, **segnala** (non correggere) le possibili discrepanze con `docs/pinout_v0.1.md` e la sezione Elettronica di `CLAUDE.md`.
4. **Non** toccare `pagina/`, `README.md`, `CHANGELOG.md`. **Non** fare `git add`, commit né push. Non lanciare gli agenti `comunicazione` e `git-readme`.
5. Rispondimi con 3 righe al massimo: cosa hai aggiornato e da dove ripartire.
6. Come ultima riga scrivi: «Ora puoi digitare `/clear` (poi `/stato` per ripartire). Commit e pagina restano per il prossimo `/fine-sessione`.»
