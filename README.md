# Elokuvien arvostelu sovellus

## Sovelluksen nykyinen tilanne

* Käyttäjä pystyy luomaan tunnuksen, kirjautumaan sisään, ja kirjautumaan ulos.
* Käyttäjät voivat lisätä, muokata ja poistaa elokuva-arvosteluitaan.
* Jokainen arvostelu sisältää elokuvan nimen, arvostelutekstin, katsomisajan, genret, ja arvosanan (1-5 tähteä).
* Käyttäjä näkee sovellukseen lisätyt arvostelut.
* Käyttäjä pystyy etsimään arvosteluita hakusanalla.
* Sovelluksessa on käyttäjäsivut, jotka näyttävät tilastoja ja käyttäjän lisäämät arvostelut.
* Käyttäjät voivat lisätä elokuvalle genrejä valmiiusta valikosta tai omia genrejä.
* Jättää palautetta muiden arvosteluista valitsemalla peukku ylös/alas ja kirjoittamalla valinnaisen kommentin.

## Sovelluksen asennus

1. Kloonaa sovellus komennolla: `git clone https://github.com/wentzelo/TIKAWE-Elokuva-Arvostelu.git`

2. (Valinnainen) Luo Python vietuaaliympäristö sovelluksen kansioon:

    Linux (Bash): `python -m venv venv` ja aktivoi `source venv/bin/activate`.

    Windows (CMD): `python -m venv venv` ja aktivoi `venv\Scripts\activate`.

3. Asenna `flask`-kirjasto: `$ pip install flask`.

4. Luo tietokannan taulut schema.sql avulla:

    `$ sqlite3 database.db < schema.sql`

    Jos haluat esitietoja voit ajaa seed.py ohjelman: `python seed.py`

5. Käynnistä sovellus seuraavalla komennolla:

    `@ flask run`

6. Siirry sovelluksen sivulle.

## Sovelluksen toiminta suurilla tietomäärillä

Sovellusta testattiin suurella tietomäärällä käyttämällä `seed.py` tiedostoa joka loi tietokantaan 10 000 käyttäjää ja 100 000 arvostelua. Aluksi se hidasti sovelluksen toimintaa etusivulla merkittävästi, koska kaikki arvostelut näytettiin yhdellä sivulla. Kun etusivulle lisättiin sivutus, ongelma ratkesi. Jopa ilman tietokantaindexiä sivun lataamisajat olivat 0.00-0.03s väliltä. 

100 000 käyttäjälle ja 1 000 000 arvostelulla sovellus kaatuu useimmiten etusivua ladatessa, ilman indexiä. Tietokantaindexien käyttöönottamisen jälkeen sivu latautuu noin 6 sekunnissa ja toimii sen jälkeen täydellisesti. Käytössä olivat `idx_posts_id`, `idx_posts_user_id`, ja `idx_users_id`.

Kuten näemme alla olevista kuvista niin latausajat eivät muuttuneet 10 000 käyttäjällä mutta 100 000 käyttäjällä indexit nopeuttivat latausta huomattavasti.

Ennen indexiä - 10 000 käyttäjää + 100 000 arvostelua:

![Performance without index 10 000](Images/image2.png)

Indexien jälkeen - 10 000 käyttäjää + 100 000 arvostelua:

![Performance with index](Images/image.png)

Ennen indexiä - 100 000 käyttäjää + 1 000 000 arvostelua:

![Performance witout index 100 000](Images/image3.png)

Indexien jälkeen - 100 000 käyttäjää + 1 000 000:

![Performance with index 100 000](Images/image4.png)

### Miten sivutus toimii

Kun käyttäjä siirtyy etusivulle vain sivukohtainen määrä arvosteluita haetaan tietokannasta `LIMIT` ja `OFFSET` ehtoja käyttämällä Esim sivulla kolme haetaan rivit 21-30.
