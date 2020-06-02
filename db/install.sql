/* First time install only */
CREATE TABLE exams (
    exam_id integer PRIMARY KEY,
    shortname text NOT NULL,
    testdescription text,
    info text,
    outfit text,
    max_time text,
    dateadded text,
    is_active integer,
    min_correct integer
    );
CREATE TABLE cases (
    case_id integer PRIMARY KEY,
    sex integer,
    age integer,
    height real,
    weight real,
    asa text
    );
CREATE TABLE questiontype (
    qt_id integer PRIMARY KEY,
    qtype text
    );
CREATE TABLE examquestions (
    question_id integer PRIMARY KEY,
    examID integer,
    question_type integer,
    question text,
    q_description text,
    answers text,
    important integer,
    FOREIGN KEY (examID)
        references exams (exam_id),
    FOREIGN KEY (question_type)
        references questiontype (qt_id)
    );
CREATE TABLE results (
    res_id integer PRIMARY KEY,
    case_id integer,
    date_completed text,
    exam_id integer,
    answers text,
    sensor text,
    is_exam integer,
    time_used text,
    student integer,
    grade integer,
    comment text,
    start_time text,
    stop_time text,
    json text,
    FOREIGN KEY (exam_id)
        references exams (exam_id),
    FOREIGN KEY (case_id)
        REFERENCES cases (case_id),
    FOREIGN KEY (student)
        REFERENCES users (user_id)
);
CREATE TABLE active_exam (
    ae_id integer PRIMARY KEY,
    exam_id integer,
    start_time text,
    room integer
);
CREATE TABLE users (
    user_id integer PRIMARY KEY,
    card_number TEXT,
    student_id integer,
    first_name TEXT,
    last_name TEXT,
    student_mail TEXT,
    exams_taken integer,
    exams_passed integer,
    exams_failed integer,
    practice_exams_done integer,
    isActive integer,
    userType integer,
    password text,
    FOREIGN KEY (userType)
        REFERENCES userTypes (id)
);
CREATE TABLE userTypes(
    id integer PRIMARY KEY,
    name text,
    access integer,
    FOREIGN KEY (id)
        REFERENCES users (userType)
);
CREATE TABLE rooms(
    server_id integer PRIMARY KEY,
    roomName text,
    room integer,
    ip text,
    firewall integer,
    password text
);
CREATE TABLE active_tablets(
    id integer PRIMARY KEY,
    uuid TEXT,
    date TEXT,
    is_active integer
);
CREATE TABLE serverStatus(
    id integer PRIMARY KEY,
    CPU text,
    RAM text,
    DISKS text,
    NETWORK text
);

INSERT INTO rooms(roomName, room, ip, firewall, password)
VALUES("testRoom",
       1,
       "192.168.1.226",
       4444,
       "MYSecurePassword"
);

INSERT INTO users(card_number, student_id, first_name, last_name, student_mail, exams_taken, exams_passed, exams_failed, practice_exams_done, isActive, userType, password)
VALUES ('1', '1', 'Admin', 'Istrator', 'admin@admin.none', 0, 0, 0, 0, 1, 3, 'IGHAdmin6');

INSERT INTO questiontype(qtype)
VALUES('Forberedelse'),
      ('Gjennomføring'),
      ('Etterarbeid');


INSERT INTO userTypes(name,access)
VALUES ('Student',0),
       ('Lærer',1),
       ('Admin',666);


INSERT INTO exams (shortname, testdescription, info, outfit, max_time, dateadded, is_active, min_correct)
VALUES (
        'OSCE Vasoaktiv infusjon',
        'Oppkobling av sprøytepumpe med noradrenalin-infusjon',
        'Studenten skal blande ut en vasoaktiv infusjon, og koble opp og starte infusjonen på sprøytepumpe ut i fra en ordinasjon|Kan forklare indikasjon for oppstart av gitt infusjon',
        'Korrekt arbeidsantrekk',
        '00:15:00',
        datetime('now', 'localtime'),
        1,
        10);
INSERT INTO cases (sex, age, height, weight, asa)
VALUES (0,35,165,64,1);
INSERT INTO examquestions (examID, question_type, question, q_description, answers,important)
VALUES (1,
        1,
        'Utfører håndhygiene',
        'No description',
        '1|0',
        0
    ),
    (
        1,
        1,
        'Finner fram nødvendig utstyr',
        'Nødvendig utstyr?',
        '1|0',
        0
    ),
    (
        1,
        1,
        'Finner fram og kontrollerer medikament',
        '',
        '1|0',
        1
    ),
    (
        1,
        1,
        'Kontrollerer utblanding/konsentrasjon, enten ifht prosedyre eller ved utregning.',
        '',
        '1|0',
        1
    ),
    (
        1,
        1,
        'Kan forklare om indikasjoner for oppstart av vasoaktiv infusjon',
        '',
        '1|0',
        0
    ),
    (
        1,
        2,
        'Trekker opp medikament og væske til utblanding med aseptisk teknikk',
        '',
        '1|0',
        0
    ),
    (
        1,
        2,
        'Ber om dobbletkontroll på utblanding',
        '',
        '1|0',
        0
    ),
    (
        1,
        2,
        'Merker sprøyte og infusjonsslange. Sprøyte minimum med medikamentnavn og konsentrasjon.',
        '',
        '1|0',
        1
    ),
    (
        1,
        2,
        'Stiller inn sprøytepumpe korrekt med hjelp av protokoll, og ber om dobbeltkontroll',
        '',
        '1|0',
        1
    ),
    (
        1,
        2,
        'Kobler evt tilbakeslagsventil og fyller infusjonsslange',
        '',
        '1|0',
        0
    ),
    (
        1,
        2,
        'Kan begrunne valg av infusjonssted og om andre infusjoner kan gå parallelt med denne',
        '',
        '1|0',
        0
    ),
    (
        1,
        2,
        'Kobler til med aseptisk teknikk',
        '',
        '1|0',
        0
    ),
    (
        1,
        2,
        'Starter infusjon med korrekt/ordinert dosering/infusjonshastighet',
        '',
        '1|0',
        1
    ),
    (
        1,
        3,
        'Dokumenterer/bekrefter at vil dokumentere',
        '',
        '1|0',
        0
    ),
    (
        1,
        3,
        'Kan forklare relevante observasjoner etter oppstart',
        '',
        '1|0',
        0
    ),
    (
        1,
        3,
        'Fjerner avfall og rydder opp',
        '',
        '1|0',
        0
    );



INSERT INTO exams (shortname, testdescription, info, outfit, max_time, dateadded, is_active, min_correct)
VALUES (
        'Endotrakeal intubasjon',
        'OSCE, AIO MAN4000 Intubasjon',
        'Studenten skal forberede til intubasjon og gjennomføre et intubasjonsforsøk.|Intubatøren skal selv lytte og verifisere korrekt tubeleie|Øsofagusintubasjon aksepteres, men dette må oppdages og studenten må angi at  prosedyren avsluttes og maskeventilasjon gjenopptas.|Må forklare gangen i en innledning, men testes kun i forberedelse og  gjennomføring av selve intubasjonsprosedyren',
        'Korrekt arbeidsantrekk',
        '00:10:00',
        datetime('now', 'localtime'),
        1,
        8);
INSERT INTO cases (sex, age, height, weight, asa)
VALUES (1,65,183,88,1);
INSERT INTO examquestions (examID, question_type, question, q_description, answers,important)
VALUES (2,
        1,
        'Finner fram nødvendig utstyr',
        'hansker',
        '1|0',
        0
    ),
    (2,
        1,
        'Sjekker laryngoskop og endotrakealtube',
        '',
        '1|0',
        1
    ),
    (2,
        1,
        'Kontrollerer sug',
        '',
        '1|0',
        1
    ),
    (2,
        1,
        'Kan forklare om preoksygenering, maske/bag-ventilasjon og det helt grunnleggende om medikamenter til innledning av anestesi.',
        '',
        '1|0',
        0
    ),
    (2,
        2,
        'Leirer pasienten optimalt',
        'ramped posistion eller sniffing posistion',
        '1|0',
        1
    ),
    (2,
        2,
        'Laryngoskoperer med bruk av venstre hånd, går ned i høyre munnvik eller midtlinjen, og identifiserer epiglottis',
        '',
        '1|0',
        0
    ),
    (2,
        2,
        'Bruker kraft i laryngoskophåntakets retning og unngår skade på tenner og lepper.',
        '',
        '1|0',
        1
    ),
    (2,
        2,
        'Får innsyn til stemmespalten og trachea',
        '',
        '1|0',
        0
    ),
    (2,
        2,
        'Fører tube ned til korrekt dybde',
        '',
        '1|0',
        0
    ),
    (2,
        2,
        'Assistent fyller luft i cuff, og kobler til anestesisirkel/bag ',
        '',
        '1|0',
        0
    ),
    (2,
        2,
        'Verifiserer korrekt tubeleie med stetoskopi (5-punkts lytting) og bevegelse, evt kapnografi om tilgjengelig.',
        '',
        '1|0',
        0
    ),
    (2,
        2,
        'Fikserer tube og gjentatt lytting dersom korrekt plassert, om ikke trekker tuben tilbake og angir at de vil gjenoopta maskeventilasjon.',
        '',
        '1|0',
        0
    );



INSERT INTO exams (shortname, testdescription, info, outfit, max_time, dateadded, is_active, min_correct)
VALUES (
        'Oppkobling TIVA-sett',
        'OSCE, Oppkobling TIVA-sett',
        'Studenten skal blande ut medikamenter (propofol/remifentanil og koble opp TIVA-sett og programmere pumpene i hht valgt medikament-protokoll|Studenten skal kunne forklare grunnbegreper ved TIVA/TCI (Cp, Cpt, Ce og Cet)',
        'Korrekt arbeidsantrekk',
        '00:15:00',
        datetime('now', 'localtime'),
        1,
        8);
INSERT INTO cases (sex, age, height, weight, asa)
VALUES (0,63,183,74,2);

INSERT INTO examquestions (examID, question_type, question, q_description, answers,important)
VALUES (3,
        1,
        'Finner fram nødvendig utstyr og medikamenter',
        '',
        '1|0',
        0
    ),
    (3,
        1,
        'Blander og trekker opp medikamenter med aseptisk prosedyre',
        '',
        '1|0',
        1
    ),
    (3,
        1,
        'Kontrollerer koblinger på TIVA-sett og ivaretar aseptikk ved håndtering',
        '',
        '1|0',
        0
    ),
    (3,
        1,
        'Kobler til sprøyter og fyller slanger, fyller infusjonssett med infusjonsvæske uten deponering av medikament i infusjonsslange',
        '',
        '1|0',
        0
    ),
    (3,
        1,
        'Kan programmere pumper med propofol og remifentanil ut fra gitt pasientcase',
        '',
        '1|0',
        0
    ),
    (3,
        1,
        'Ber om dobbeltkontroll på utblanding/programmering',
        '',
        '1|0',
        1
    ),
    (3,
        1,
        'Kan forklare forskjell på Cp, Cpt, Ce og Cet',
        '',
        '1|0',
        0
    ),
    (3,
        1,
        'Kan foreslå oppstartstarget for enten sedasjon eller innledning. ',
        '',
        '1|0',
        0
    ),
    (3,
        1,
        'Kan forklare hva som kan gjenbrukes i et TIVA-sett/regler for gjenbruk av medikamenter.',
        '',
        '1|0',
        0
    );



INSERT INTO exams (shortname, testdescription, info, outfit, max_time, dateadded, is_active, min_correct)
VALUES (
        'Arteriekran, kalibrering og blodprøvetaking',
        'OSCE, AIO MIN4000 /MAN4000 arteriekran  0-ing og blodprøvetaking',
        'Kaliberering av arteriekran til atmosfærisk trykk|Blodprøvetaking fra arteriekran|Kan forklare hvordan koblinger håndteres korrekt ved daglig bruk',
        'Korrekt arbeidsantrekk',
        '00:15:00',
        datetime('now', 'localtime'),
        1,
        13);
INSERT INTO examquestions (examID, question_type, question, q_description, answers,important)
VALUES (4,
        1,
        'Utfører håndhygiene',
        'Nulling av arterietrykksett:',
        '1|0',
        0
    ),
    (4,
        1,
        'Finner fram nødvendig utstyr',
        'Nulling av arterietrykksett:',
        '1|0',
        0
    ),
    (4,
        2,
        'Stiller inn høyde på sensor i korrekt høyde i forhold til høyre atrie ',
        'Nulling av arterietrykksett:',
        '1|0',
        1
    ),
    (4,
        2,
        'Vrir treveiskran i korrekt stilling for å åpne mellom luft og transduser',
        'Nulling av arterietrykksett:',
        '1|0',
        1
    ),
    (4,
        2,
        'Fjerner propp på treveiskran for å åpne til luft',
        'Nulling av arterietrykksett:',
        '1|0',
        0
    ),
    (4,
        2,
        'Trykker på 0- knapp på scopet og ser at linjen går ned til null på ABP',
        'Nulling av arterietrykksett:',
        '1|0',
        0
    ),
    (4,
        2,
        'Ny steril propp settes i treveiskran og det åpnes mellom pasient og flushvæske',
        'Nulling av arterietrykksett:',
        '1|0',
        0
    ),
    (4,
        2,
        'Utfører håndhygiene, bruker hansker',
        'Blodgass:',
        '1|0',
        0
    ),
    (4,
        2,
        'Stenger den røde kranen ved transduseren mot flushing',
        'Blodgass:',
        '1|0',
        0
    ),
    (4,
        2,
        'Aspirere blod med egen sprøyte ved transduseren',
        'Blodgass:',
        '1|0',
        0
    ),
    (4,
        2,
        'Desinfiserer prøvetakingsmembran hvor prøvesprøyten skal settes inn',
        'Blodgass:',
        '1|0',
        0
    ),
    (4,
        2,
        'Aspirerer ønsket mengde blod og fjern sprøyte ',
        'Blodgass:',
        '1|0',
        0
    ),
    (4,
        2,
        'Åpner den røde kranen ved transduseren for flushing',
        'Blodgass:',
        '1|0',
        0
    ),
    (4,
        2,
        'Flush systemet ved å klemme sammen vingene på transduseren.',
        'Blodgass:',
        '1|0',
        0
    ),
    (4,
        3,
        'Fjerner avfall og rydder opp',
        '',
        '1|0',
        0
    );
