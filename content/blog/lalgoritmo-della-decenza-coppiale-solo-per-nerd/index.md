---
title: L'algoritmo della decenza coppiale (solo per nerd!)
date: '2013-10-29'
draft: false
categories:
- riflessioni
tags:
- coppia
- de-filippi
- decenza
- idiozie
- riflessioni
original_url: https://www.danielebailo.it/2013/10/29/lalgoritmo-della-decenza-coppiale-solo-per-nerd/
migration_source: wordpress-personale
cover: /uploads/2013/10/1024px-Aptenodytes_patagonicus_-family_-Edinburgh_Zoo-8a-1.jpg
---

RIESUMO UN POST DI DUBBIO VALORE ESISTENZIALE (ma con qualche possibilità cabarettistica) SCRITTO QUANDO C'ERA TANTO, TANTO BISOGNO DI VACANZA...

Il delirio che state per leggere (a vostro rischio e pericolo) è conseguenza di:

- il relax di una mini vacanza in Corsica in cui l'aerofagia mentale è riuscita ad infiltrarsi nelle fitte trame – normalmente impenetrabili - delle soglie dell'autocontrollo, abbassate a causa del clima estivo e dello spirito vacanziero

- il caldo insopportabile della capitale che proibisce qualsiasi tipo di attività riposatoria a causa dell'appiccicume sospeso nell'aria. Chi si stende sul materasso è perduto, e rischia di annegare nei prodotti dei propri processi traspiratori.

- il tentativo di dare una risposta alla domanda che molti si pongono quando, incontrando un potenziale partner stabile, pensano “Ma non sarà troppo giovane?” oppure “ma non sarà troppo maturo/a?”.

[

![Ghiacciolo-squagliato](/uploads/2013/10/ghiacciolo-squagliato.jpe)

](/uploads/2013/07/ghiacciolo-squagliato.jpeg) ecco come può ridurti il caldo

Ecco, per non lasciare al caso, all'interpretazione personale, agli umori momentanei e ai pruriti intranatichei la risposta, proviamo a creare un algoritmo che permetta di capire se si è entro un certo limite imposto dalla decenza.

Ammesso che la parola “decenza” abbia ancora un significato - ne dubito ogni volta che vedo la [de Filippi](https://twitter.com/colvieux/status/203576076037914625) condurre una qualsiasi delle sue trasmissioni. Motivo per cui i risultati del presente lavoro non sono applicabili a lei.

Chiariamo subito che se non siete soggetti paranoici, se vi sentite liberi, senza manie e non avete bisogno di definire ogni dettaglio della vostra vita, allora potete anche saltare il resto e fare un po' come vi pare.

(Io non sono tra questi e continuo.)

Se invece siete dei nerd dell'organizzazione esistenziale, allora andate avanti tranquilli ed i risultati del presente lavoro contribuiranno a placare le vostre ansie causate da stati paranoidi e ad alimentare nuovi ragionamenti che molto probabilmente indurranno nuovi e più numerosi stati ansiogeni e di alienazione (con vostra grande goduria).

L'agoritmo è modificabile, ovviamente, e anzi invito l'intera comunità scientifica a contribuire per renderlo sempre più generale e applicabile ad ogni situazione (pure alla de Filippi).

P**remessa uno**: si prende in considerazione un rapporto di coppia stabile o semi stabile. Quindi l'avventura del 50enne con la diciottenne non è oggetto dell'algoritmo.

**Premessa due:**si considerano solo maggiorenni (così mi svincolo pure da possibili conseguenze legali, tiè).

[

![code](/uploads/2013/10/code.jpe)

](/uploads/2013/07/code.jpeg)Quello che cercheremo di definire, nei limiti imposti da questa premessa, è una formula che permette di *determinare in una coppia la differenza di età massima oltre la quale scatta il campanello dell'indecenza*.

Per esempio, un uomo di trenta anni che ha un partner di ottantaquattro è da considerarsi poco decente. Una donna di quarantacinque con un diciottenne pure.

Il concetto base è che la differenza di età non può essere fissata a priori. Non ha senso dire “ci devono essere non più di 10 anni di differenza. Infatti tra i 20 e i 30 anni, dieci anni sono tantissimi. Mentre tra 35 e 45 la differenza è molto meno marcata.

*Da questo deduciamo subito che la differenza di età aumenta all'aumentare dell'età dei partners*

Quindi, definendo SD come la soglia della decenza (massima differenza di età), possiamo scrivere:

**SD=f(*es*),**   dove *es*sta per *età del soggetto*.

***La soglia della decenza è funzione dell'età del soggetto (non è fissata).***

Andando un po' per tentativi (ah, le scienze sperimentali), inizialmente avevo definito f(es) come

**f(es)=1/3\*es**

Tale funzione non è poi male, ma per i valori più piccoli di *es* non è convincente.

Ad esempio nei casi di seguito (un estratto dell'intero plot) , se uno ha 27 anni, la soglia inferiore della decenza ci dice che può stare con un diciottenne... e di che parlano?

| *ETA (es)* | *ETA min/max del partner (es**±* f(*es*) ) | *Commento* |

| --- | --- | --- |

| 27 | 18 o 36 | Di che parlano? Del compito in classe... |

| 30 | 20 o 40 | Idem. Anche se questo caso si verifica più spesso, non è esageratemente insolito |

Provando a divertirsi con gli esponenziali si può generare qualcosa del genere:

**f(es)=1/3\*(es^2)**

Ma gli esempi non sono convincenti a causa della poca longevità dell'essere umano:

| *ETA (*es) | *ETA min/max del partner (*es*2* - f(*es*)) | *Commento* |

| --- | --- | --- |

| 13 | 112 | Centododici Anni! |

Dopo qualche ragionamento e discussione, una buona soluzione sembra essere la seguente:

**f(es)=1/4\*es**

Infatti i valori sono tutti ragionevoli. Alcuni forse un po' restrittivi, ma si potrebbe introdurre una funzione di errore.

Qualche valore:

| *ETA (*es) | *ETA min/max del partner (es**±* f(*es*) ) | *Commento* |

| --- | --- | --- |

| 27 | 20 o 33 | Dai, alla fine se va bene entrambi lavorano o studiano |

| 30 | 22 o 38 | Idem. |

| 35 | 26 o 44 | Tipico caso, il primo, dell'uomo che oramai maturo sa quello che vuole e si trova una ragazzetta sveglia che pure lei sa quello che vuole. Ma anche il secondo... |

| 40 | 30 o 50 | Ed anche il caso di S. è salvo, rientra nella decenza!! |

| 50 | 37,5 o 63 | Si trovano alcuni di questi casi. |

Quindi vorrei ufficialmente sottoporre questo risultato alla comunità scientifica (indubbiamente interessata a questo vitale argomento), esprimibile tramite il seguente predicato:

*Non si oltrepassa la soglia della decenza quando la differenza di età con il proprio partner non supera la soglia individuata dalla seguente equazione:*

**f(es)=1/4\*es**

Detto questo non mi resta che andare a guardare “Amici”, quel bellissimo programma della De Filippi... (chissà se la sua coppia rispetta l'algoritmo)

[

![Maurizio-Costanzo-e-Maria-De-Filippi](/uploads/2013/10/maurizio-costanzo-e-maria-de-filippi.jpe)

](/uploads/2013/07/maurizio-costanzo-e-maria-de-filippi.jpeg)

Header image Di Dave Morris [CC BY 2.0 (http://creativecommons.org/licenses/by/2.0)], attraverso [Wikimedia Commons 

![](https://commons.wikimedia.org/wiki/File%3AAptenodytes_patagonicus_-family_-Edinburgh_Zoo-8a.jpg)

](https://commons.wikimedia.org/wiki/File%3AAptenodytes_patagonicus_-family_-Edinburgh_Zoo-8a.jpg)
