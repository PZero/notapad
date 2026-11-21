---
description: Salva lo stato della sessione nei documenti del progetto e pubblica su GitHub
model: sonnet
---

Chiudiamo la sessione. Senza rileggere file che non servono:

1. Aggiorna `docs/STATO.md`: data di oggi, fase attuale, cosa è stato fatto in questa sessione, cosa è in corso, prossimi passi, cosa è in pausa. **Riscrivi** il file tenendolo sotto le 60 righe: è una fotografia dello stato, non un diario.
2. Aggiungi a `docs/DECISIONI.md` le decisioni prese oggi (una riga nella tabella: data, decisione, motivazione). Non riscrivere quelle vecchie. Aggiorna `docs/DOMANDE-APERTE.md`: togli le domande risolte, aggiungi le nuove.
3. Se sono cambiati componenti, pin o collegamenti, verifica che siano allineati `docs/pinout_v0.1.md`, `jlc/notapad_v0.1_BOM_JLC.csv`, `jlc/notapad_v0.1_collegamenti.csv`, la sezione Elettronica di `CLAUDE.md` e, se esiste, `firmware/`. Se c'è una discrepanza, correggi il documento o segnalala.
4. Rigenera i file prodotti da script che dipendono da quanto è cambiato (catena in `kicad/` descritta in `CLAUDE.md`, export in `kicad/fab_out/` con `genera_fab.py`): su GitHub devono finire le versioni aggiornate. Se ci sono test (firmware, app), eseguili e riporta l'esito.
5. **Comunicazione (PR).** Lancia l'agente `comunicazione` in primo piano, **non in background**, e **aspetta il suo rapporto prima di passare al punto 6**. Passagli questo brief, compilato con i fatti della sessione:
   ```
   Fine sessione del <data>. Novità di oggi (fatti, non intenzioni):
   - <sviluppo 1: cosa è cambiato e perché>
   - <sviluppo 2 ...>
   Decisioni nuove: <righe aggiunte oggi a docs/DECISIONI.md>
   In corso / prossimi passi / in pausa: <da docs/STATO.md>
   Immagini nuove da mostrare (se ci sono): <percorsi, es. kicad/anteprima.png, render/...>

   Compiti:
   1. pagina/index.html, sezione #progress "Progress and next steps": aggiorna Done / In progress / Next / On hold con le novità di oggi.
   2. pagina/index.html, sezione #history "Project history": timeline in ordine cronologico inverso, costruita da `git log --date=short --pretty="%h|%ad|%s"`; raggruppa per giorno, riscrivi i messaggi in frasi leggibili per il pubblico (non copiare gli hash grezzi, al massimo un link al commit su GitHub), salta i commit puramente tecnici (typo, formattazione). Aggiungi in cima la voce di oggi con le novità di questa sessione, anche se il commit non è ancora fatto. Se la sezione non esiste, creala nello stile della pagina.
   3. README.md: allinea "Status and roadmap" e "What changed" alle novità; aggiungi o aggiorna la sezione "Project history" con le ultime 5 tappe e un link a #history della pagina.
   4. Controlla che link e immagini citati esistano e che non ci siano dati personali.
   Non fare commit: li fa git-readme subito dopo.
   ```
   Se `comunicazione` segnala un problema (dato incerto, privacy, link rotto), risolvilo o riportamelo prima di andare avanti.
6. Solo dopo il rapporto di `comunicazione`, affida all'agente `git-readme`, con la stessa sintesi:
   - aggiornare `CHANGELOG.md` (voci nuove in inglese);
   - **il repository `PZero/notapad` è PUBBLICO**: controllo privacy prima del push (chiavi, token, password, `.env`, registrazioni audio, email, percorsi locali con il nome utente Windows, dati personali); se trova qualcosa, si ferma e riporta;
   - `git add -A` di tutti i file del progetto (render, PDF e file JLC compresi; fuori solo quanto è in `.gitignore`);
   - commit (messaggi in inglese) e push su `origin main`;
   - verificare con `git status` che sia tutto pulito, con `git ls-remote origin` che `main` remoto punti al commit locale e, se è cambiata `pagina/`, che il workflow Pages sia andato a buon fine (`gh run list`).
   Da sessione cloud: branch `cloud/<data>-<argomento>` + Pull Request.
7. Rispondimi con 5 righe al massimo: cosa è stato salvato (commit e remote) e da dove ripartire la prossima volta.
8. Come ultima riga scrivi: «Ora puoi digitare `/clear` (poi `/stato` per ripartire).» Un comando non può svuotare la chat da solo: `/clear` va digitato dall'utente.
