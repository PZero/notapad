# Piano editoriale social – notªpad

Account: Instagram, YouTube e TikTok **@notapadlabs**. Testi dei post in **inglese** (pubblico internazionale, sponsor esteri); le note di lavoro qui in italiano.

## Ritmo sostenibile

| Cosa | Dove | Frequenza | Sforzo |
|---|---|---|---|
| Reel / Short verticale 15–40 s | Instagram Reel + YouTube Short (stesso file) | **1 a settimana** (martedì) | medio |
| Carosello 5–8 immagini | Instagram | **1 a settimana** (venerdì) | basso |
| Storie (foto al banco, sondaggi) | Instagram | 2–3 a settimana, quando capita | minimo |
| Video lungo 5–10 min | YouTube | **1 al mese**, solo a una tappa vera | alto |

**Lancio (deciso il 25/11):** nei primi giorni 4–5 post a settimana, per non lasciare il profilo con un solo contenuto. Poi si torna al ritmo qui sopra.

| Data | Post | Dove |
|---|---|---|
| mer 25/11 | 1 · carosello «Meet notªpad» | IG + TikTok (programmati) |
| ven 27/11 | 3 · carosello «Why we are building this» (evergreen) | IG |
| sab 28/11 | 4 · Reel «Pick the finish» (voto 1–6) | IG + YT Short + TikTok |
| lun 30/11 | 5 · carosello «Where do your recordings go?» | IG |
| mar 1/12 | 2 · Reel «What if your ideas never got lost again?» | IG + YT Short + TikTok (programmati) |
| gio 3/12 | 6 · Reel «It sleeps until you speak» | IG + YT Short + TikTok |
| sab 5/12 | 7 · carosello «16.5 × 38 mm, four layers» | IG |

Ora 18:30 per tutti. Ogni giorno una Storia (anche solo la condivisione del post). Il post 3 è **evergreen**: si ripropone nei periodi senza novità.

**La macchina:** una sessione di 2 ore ogni due settimane produce 2 Reel + 2 caroselli (Claude prepara testi, grafiche e scalette; voi girate le clip al banco). Si programma tutto in Meta Business Suite (gratis). Regola: meglio due post buoni a settimana per sei mesi che sette in una settimana e poi silenzio.

**Ogni post finisce con una sola chiamata all'azione**, a rotazione: segui · stella su GitHub · Ko-fi · commenta/vota.

## I 5 temi (rotazione)

1. **Il perché** – il problema (le idee si perdono, i registratori AI chiudono i dati nel loro cloud) e la visione (l'AI la scegli tu, MCP aperto).
2. **Dentro la scheda** – ingegneria spiegata semplice: 4 strati in 16 × 38 mm, due microfoni, latch della batteria, tocco a "stretta".
3. **Diario di bordo** – tappe reali, anche gli errori: ordine JLC, arrivo schede, prima accensione, prima colata.
4. **Aperto e tuo** – open source, privacy, trascrizione sul dispositivo, nessun abbonamento.
5. **Con voi** – sondaggi (finitura, colore LED), ringraziamenti ai sostenitori, richieste di aiuto.

## I primi 9 post (stato al 25/11)

| # | Tipo | Tema | Contenuto | Stato |
|---|---|---|---|---|
| 1 | Carosello | Perché | **"Meet notªpad."** | pronto, programmato 25/11 |
| 2 | Reel | Perché | **"What if your ideas never got lost again?"** | pronto, programmato 1/12 |
| 3 | Carosello | Perché / Con voi | **"Why we are building this."** 7 slide: problema, perché non basta ciò che esiste, 4 principi, riscontri dei futuri utenti (i più importanti) con 4 domande, «How you can help» (riscontri, condivisione, Ko-fi, sponsor aziendali). **Evergreen**, senza date: riproponibile | pronto (`post/03_why-it-matters`) |
| 4 | Reel | Con voi | **"Pick the finish."** 6 finiture, voto 1–6 nei commenti | pronto (`post/04_reel-pick-the-finish`) |
| 5 | Carosello | Aperto e tuo | **"Where do your recordings go?"** confronto senza marchi, percorso dei dati, server anche self-hosted | pronto (`post/05_where-recordings-go`) |
| 6 | Reel | Dentro la scheda | **"It sleeps until you speak."** due microfoni, risveglio acustico (senza nome del componente) | pronto (`post/06_reel-two-microphones`) |
| 7 | Carosello | Dentro la scheda | **"16.5 × 38 mm, four layers."** zone A/B/C, 4 strati, scheda generata dal codice, stella su GitHub | pronto (`post/07_inside-the-board`) |
| 8 | Carosello | Diario di bordo | **"Ordering our first boards."** quando c'è l'ordine; ultima slide Ko-fi | dopo l'ordine |
| 9 | Reel | Diario di bordo | **arrivo delle schede**: unboxing 20 s, "Next: first power-on." | da girare |

Script: `post/genera_postNN.py` e `post/genera_reelNN.py`, funzioni comuni in `post/comune.py`.

## Tappe che diventano video lunghi YouTube
Prima accensione · prima registrazione trascritta · prima colata di resina · un giorno intero al collo.

## Regole
- Niente volti, nomi o città (repo pubblico): mani, banco, oggetto.
- Niente cifre del budget personale; obiettivo Ko-fi sì.
- Hashtag fissi (5–8): #opensourcehardware #wearabletech #maker #electronics #pcbdesign #kicad #ai #buildinpublic.
- Ogni tappa → anche Reddit (r/electronics, r/PrintedCircuitBoard) e Hackaday.io, dove guardano gli sponsor.
