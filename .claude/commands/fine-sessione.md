---
description: Salva lo stato della sessione nei documenti del progetto e pubblica su GitHub
model: sonnet
---

Chiudiamo la sessione. Senza rileggere file che non servono:

1. Aggiorna `docs/STATO.md`: data di oggi, fase attuale, cosa è stato fatto in questa sessione, cosa è in corso, prossimi passi, cosa è in pausa. **Riscrivi** il file tenendolo sotto le 60 righe: è una fotografia dello stato, non un diario.
2. Aggiungi a `docs/DECISIONI.md` le decisioni prese oggi (una riga nella tabella: data, decisione, motivazione). Non riscrivere quelle vecchie. Aggiorna `docs/DOMANDE-APERTE.md`: togli le domande risolte, aggiungi le nuove.
3. Se sono cambiati componenti, pin o collegamenti, verifica che siano allineati `docs/pinout_v0.1.md`, `jlc/notapad_v0.1_BOM_JLC.csv`, `jlc/notapad_v0.1_collegamenti.csv`, la sezione Elettronica di `CLAUDE.md` e, se esiste, `firmware/`. Se c'è una discrepanza, correggi il documento o segnalala.
4. Rigenera i file prodotti da script che dipendono da quanto è cambiato (`kicad/genera_kicad.py`, export JLC in `kicad/jlc_out/`): su GitHub devono finire le versioni aggiornate. Se ci sono test (firmware, app), eseguili e riporta l'esito.
5. Affida all'agente `comunicazione`, con una sintesi di cosa è cambiato oggi, l'allineamento di `README.md` (in inglese) e della pagina `pagina/index.html` (GitHub Pages, sezione Progress) allo stato reale.
6. Affida all'agente `git-readme`, con la stessa sintesi:
   - aggiornare `CHANGELOG.md` (voci nuove in inglese);
   - **il repository `PZero/notapad` è PUBBLICO**: controllo privacy prima del push (chiavi, token, password, `.env`, registrazioni audio, email, percorsi locali con il nome utente Windows, dati personali); se trova qualcosa, si ferma e riporta;
   - `git add -A` di tutti i file del progetto (render, PDF e file JLC compresi; fuori solo quanto è in `.gitignore`);
   - commit (messaggi in inglese) e push su `origin main`;
   - verificare con `git status` che sia tutto pulito, con `git ls-remote origin` che `main` remoto punti al commit locale e, se è cambiata `pagina/`, che il workflow Pages sia andato a buon fine (`gh run list`).
   Da sessione cloud: branch `cloud/<data>-<argomento>` + Pull Request.
7. Rispondimi con 5 righe al massimo: cosa è stato salvato (commit e remote) e da dove ripartire la prossima volta.
8. Come ultima riga scrivi: «Ora puoi digitare `/clear` (poi `/stato` per ripartire).» Un comando non può svuotare la chat da solo: `/clear` va digitato dall'utente.
