# -*- coding: utf-8 -*-
import json, re, os
S=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'
OE=json.load(open(S+'images/manifest.json'))['oeuvres']

NOM='Suzanne Somogyi'
SOUS='Une mémoire du bijou contemporain français'
DATES='15 au 24 octobre 2026'
GALERIE='Galerie Amira Sliman Jewellery'
CARTE='https://www.google.com/maps/search/?api=1&amp;query=Galerie+Amira+Sliman%2C+9+rue+Ramey%2C+75018+Paris'
IG_GALERIE='galerieamiraslimanjewellery'

# EXPO : texte du projet PB26 d Amira Sliman (contenu/02_le_projet_PB26.txt), nom ecrit Somogyi comme sur l affiche. BIO : page officielle Parcours Bijoux 2026 (contenu/00_exposition_et_biographie.txt)
EXPO=["Ce projet d’exposition est né d’une rencontre marquante avec Monique et Jean Laurette, couple de créateurs de bijoux. Installés à Paris à leurs débuts, ils croisent la route de Courrèges, exposent aux côtés de Jean Vendome ou encore de Dinh Van. Au fil de nos échanges, ils me racontent leur parcours, leurs collaborations. Ils me racontent une partie de l’histoire du bijou contemporain français, passionnante et méconnue.",
 "Parmi les figures de cette scène, Suzanne Somogyi occupe une place singulière. Elle développe un style audacieux et reconnaissable, expérimente des matériaux novateurs pour l’époque tels que l’aluminium ou le plexiglas.",
 "J’ai rencontré Suzanne lors d’une exposition commune quelques mois avant sa disparition à l’âge de 49 ans. Son énergie créative m’a profondément marquée. Elle laisse une œuvre riche, puissante, pourtant largement ignorée.",
 "À travers cette exposition, je souhaite rendre hommage à Suzanne Somogyi et, plus largement, interroger le devenir de ces créateurs et de leurs œuvres. Que reste-t-il de ces pionniers du bijou contemporain en France, lorsque la médiatisation fait défaut ?",
 "Avec l’aide de son mari, j’ai sélectionné une centaine de pièces, représentatives de son univers artistique et mémoire de son époque. Cette exposition se veut à la fois un hommage, une redécouverte, et une reconnaissance nécessaire à une artiste majeure du bijou contemporain français."]
BIO=["Née le 2 novembre 1950 en Hongrie, elle se forme artistiquement en section bijoux au secondaire puis, durant cinq années, à l’École Supérieure d’Art.",
 "Arrivée à Paris en 1976, elle participe à des expositions collectives. En 1979, première exposition personnelle, Galerie Monade. Elle choisit de ne réaliser que des pièces uniques, explore et associe les matériaux : plexiglas, aluminium, émaux, galets taillés, associés dans des bijoux aux formes très géométriques et très pures."]

NB=' '   # espace fine insecable : francais avant : ; ! ? et dans les guillemets
def typo(s):
    s=re.sub(r'(?<=\S) (?=[:;!?»])', NB, s)
    s=s.replace('« ','«'+NB)
    return s

FL='<svg class="fl" viewBox="0 0 12 12" aria-hidden="true"><path d="M2.6 9.4 9.4 2.6M4.3 2.6h5.1v5.1"/></svg>'
IGSVG='<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2.4" y="2.4" width="19.2" height="19.2" rx="5.4"/><circle cx="12" cy="12" r="4.6"/><circle class="d" cx="17.6" cy="6.4" r="1.15"/></svg>'

LIENS=[('pieces','Pièces'),('carnet','Carnet'),('galerie','La galerie')]
nav=''.join('<a href="#%s">%s</a>'%l for l in LIENS)

# echelle commune : ECHELLE_CM centimetres reels = toute la largeur de la page ; chaque piece garde sa taille relative
ECHELLE_CM=30.0
RANGS=[[0,1],[3,2],[4,5],[6]]      # une grande piece et une petite par rang, posees sur la meme ligne
n=len(OE)
figs=[]
for i,o in enumerate(OE,1):
    mat='<p>%s</p>'%o['matiere'] if o['matiere'] else ''
    figs.append('''
  <figure class="piece__im" style="--w:{pc:.1f}%" role="button" tabindex="0" aria-label="Voir la pièce {i:02d} en grand"
          data-full="{plein}" data-bg="{bg}" data-titre="{titre}" data-mat="{m}" data-cred="" data-nom="{nom}">
   <img src="{file}" width="{w}" height="{h}" alt="{titre}, {nom}" loading="lazy" decoding="async">
   <figcaption>
    <h3>{titre}</h3>
    {mat}
    <span class="zoom">Voir en grand {fl}</span>
   </figcaption>
  </figure>'''.format(pc=o['cadre_cm']/ECHELLE_CM*100,i=i,n=n,plein=o['plein'],bg=o['bg'],titre=o['titre'],m=o['matiere'],nom=NOM,
                      file=o['file'],w=o['w'],h=o['h'],mat=mat,fl=FL))

expo=''.join('<p>%s</p>'%p for p in EXPO)+'<p class="credit" style="margin-top:16px">Amira Sliman</p>'
bio=''.join('<p>%s</p>'%p for p in BIO)

DESC=NOM+'. '+SOUS+'. '+GALERIE+', 9 rue Ramey, 75018 Paris. '+DATES+'. Vernissage le 17 octobre à partir de 18h. Parcours Bijoux Paris 2026.'

JSONLD='''<script type="application/ld+json">
{"@context":"https://schema.org","@type":"ExhibitionEvent","name":"Suzanne Somogyi, une mémoire du bijou contemporain français",
"description":"Exposition de bijou contemporain, Parcours Bijoux Paris 2026.",
"startDate":"2026-10-15","endDate":"2026-10-24",
"eventStatus":"https://schema.org/EventScheduled","eventAttendanceMode":"https://schema.org/OfflineEventAttendanceMode",
"location":{"@type":"Place","name":"Galerie Amira Sliman Jewellery","address":{"@type":"PostalAddress","streetAddress":"9 rue Ramey","postalCode":"75018","addressLocality":"Paris","addressCountry":"FR"}},
"performer":[{"@type":"Person","name":"Suzanne Somogyi"}],
"organizer":{"@type":"Organization","name":"d’un bijou à l’autre"},
"superEvent":{"@type":"Event","name":"Parcours Bijoux Paris 2026","startDate":"2026-10-01","endDate":"2026-10-31","url":"https://www.parcoursbijoux.com"},
"subEvent":[
 {"@type":"Event","name":"Vernissage, Suzanne Somogyi","startDate":"2026-10-17T18:00:00+02:00","location":{"@type":"Place","name":"Galerie Amira Sliman Jewellery","address":"9 rue Ramey, 75018 Paris"}}]}
</script>'''

SITE='https://raouf-png.github.io/suzanne-somogyi/'   # adresse GitHub Pages
HEAD='''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Suzanne Somogyi · Parcours Bijoux 2026</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#ffffff">
<meta property="og:type" content="website">
<meta property="og:title" content="Suzanne Somogyi · Parcours Bijoux Paris 2026">
<meta property="og:description" content="Vous êtes invité(e)s. {desc}">
<meta property="og:locale" content="fr_FR">
<meta property="og:url" content="{site}">
<meta property="og:image" content="{site}images/affiche/affiche_suzanne_somogyi.jpg">
<meta property="og:image:width" content="1080">
<meta property="og:image:height" content="1350">
<link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png">
<link rel="icon" type="image/png" sizes="512x512" href="favicon-512.png">
<link rel="apple-touch-icon" href="favicon-180.png">
<link rel="stylesheet" href="style.css?v=20260919k">
{jsonld}
</head>
<body>
<script>document.documentElement.classList.add('js')</script>

<header class="bar">
 <a class="bar__b" href="#top">Suzanne Somogyi</a>
 <nav class="bar__n">{nav}</nav>
</header>
<div class="fil" aria-hidden="true">
 <a class="fil__b" href="#top">S. Somogyi</a>
 <nav class="fil__n">{nav}</nav>
</div>
'''

BODY='''
<main>

<section class="hero" id="top">
 <p class="hero__k lbl">Parcours Bijoux Paris 2026</p>
 <h1>Suzanne Somogyi.</h1>
 <div class="hero__sub">
  <em>{sous}</em>
 </div>

 <p class="invit">Vous êtes invité(e)s.</p>

 <div class="meta">
  <div><span class="lbl">Dates</span><p>{dates}</p></div>
  <div><span class="lbl">Lieu</span>
   <p><a class="carte" href="{carte}"
         target="_blank" rel="noopener">{galerie}<br>9 rue Ramey<br>75018 Paris<span class="k">Voir sur la carte {fl}</span></a></p></div>
  <div><span class="lbl">Horaires</span><p>Du mardi au samedi, 11h30 à 19h<br>Ouverture exceptionnelle dimanche 18 octobre</p></div>
  <div><span class="lbl">Vernissage</span><p>Samedi 17 octobre, de 18h à 20h30</p><a class="k" href="agenda/vernissage.ics">Ajouter à l’agenda {fl}</a></div>
 </div>
</section>

<section id="suzanne-somogyi" class="ancre">
 <div class="split">
  <div><span class="lbl">Suzanne Somogyi</span></div>
  <div class="prose">{bio}</div>
 </div>
 <div class="rule"></div>
</section>

<section id="exposition" class="ancre">
 <div class="split">
  <div><span class="lbl">L’exposition</span></div>
  <div class="prose">{expo}</div>
 </div>
 <div class="rule"></div>
</section>

<section class="affiche">
 <figure>
  <img src="images/affiche/affiche_suzanne_somogyi.jpg" width="1080" height="1350" alt="Affiche de l’exposition Suzanne Somogyi, Parcours Bijoux Paris 2026" decoding="async">
  <figcaption><span class="lbl">Parcours Bijoux Paris 2026</span><span class="lbl">Affiche de l’exposition</span></figcaption>
 </figure>
</section>

<section id="parcours" class="ancre">
 <div class="split">
  <div><span class="lbl">Parcours Bijoux</span></div>
  <div class="prose">
   <p>L’exposition fait partie de Parcours Bijoux, le rendez-vous parisien du bijou
   contemporain porté par l’association d’un bijou à l’autre depuis 2011.</p>
   <p>Pour sa cinquième édition, du 1<sup>er</sup> au 31 octobre 2026, Parcours Bijoux
   réunit 33 expositions et plus de 200 artistes dans toute la ville : galeries, musées,
   écoles, centres culturels et ateliers d’artistes, d’une rive à l’autre. S’y ajoutent
   un colloque international, des performances et des rencontres.</p>
   <p><a class="lien" href="https://www.parcoursbijoux.com" target="_blank" rel="noopener">parcoursbijoux.com {fl}</a></p>
  </div>
 </div>
 <div class="rule"></div>
</section>

<section class="artiste" id="pieces">
 <div class="artiste__h"><h2>Pièces</h2><span>{n:02d} pièces</span></div>
 <div class="galerie">{figs}
 </div>
</section>

<section class="artiste" id="carnet">
 <div class="artiste__h"><h2>Carnet</h2><span>Recherches</span></div>
 <figure class="carnet">
  <a href="images/carnet/carnet_01.jpg" target="_blank" rel="noopener"><img src="images/carnet/carnet_01_m.jpg" width="1500" height="1215" alt="Double page d’un carnet de Suzanne Somogyi : croquis de bagues" loading="lazy" decoding="async"></a>
  <figcaption><p>Double page d’un carnet de Suzanne Somogyi. Recherches de bagues au stylo rouge et noir, dessins découpés et collés, notes manuscrites.</p></figcaption>
 </figure>
</section>

<section id="galerie" class="ancre lieu">
 <div class="rule"></div>
 <div class="lieu__h"><span class="lbl">La galerie</span></div>
 <figure class="lieu__plan">
  <a href="{carte}" target="_blank" rel="noopener" aria-label="Ouvrir l’adresse de la galerie dans Google Maps">{plan}</a>
  <figcaption><span class="lbl">Paris 18e, quartier de Clignancourt</span><span class="lbl">Fond de carte © OpenStreetMap</span></figcaption>
 </figure>
 <div class="lieu__c">
  <img class="logo" src="images/logo/galerie_amira_sliman.png" width="743" height="239" alt="{galerie}" loading="lazy" decoding="async">
  <p><a class="carte" href="{carte}" target="_blank" rel="noopener">9 rue Ramey<br>75018 Paris<span class="k">Voir sur la carte {fl}</span></a></p>
  <p><a class="lien" href="https://www.instagram.com/{igg}/" target="_blank" rel="noopener">@{igg} {fl}</a></p>
 </div>
</section>

</main>

<div class="vue" id="vue" hidden>
 <span class="lbl vue__k" id="vueK"></span>
 <button class="vue__x" aria-label="Fermer">&#215;</button>
 <div class="vue__s"><img id="vueIm" alt=""></div>
 <div class="vue__c">
  <div><h3 id="vueT"></h3><p id="vueM"></p><p class="credit" id="vueC"></p></div>
  <div class="vue__n">
   <button type="button" id="vuePrec" aria-label="Pièce précédente"><svg viewBox="0 0 18 18" aria-hidden="true"><path d="M11.5 3 5.5 9l6 6"/></svg></button>
   <button type="button" id="vueSuiv" aria-label="Pièce suivante"><svg viewBox="0 0 18 18" aria-hidden="true"><path d="M6.5 3l6 6-6 6"/></svg></button>
  </div>
 </div>
</div>

<div class="editbar"><span>Mode texte</span><button type="button" id="edCopie">Copier les textes</button><button type="button" id="edRaz">Tout remettre</button><span>Cmd A pour quitter</span></div>

<footer>
 <div class="foot">
  <div><span class="lbl">Exposition</span><p>{nom}<br>{dates}<br>{galerie}</p></div>
<div class="foot__ig">
   <span class="lbl">Instagram</span>
   <div class="igs">
    <a class="ig" href="https://www.instagram.com/{igg}/" target="_blank" rel="noopener">
     {igsvg}
     <span class="ig__n">Galerie Amira Sliman</span><span class="ig__h">@{igg}</span></a>
    <a class="ig" href="https://www.instagram.com/parcoursbijoux/" target="_blank" rel="noopener">
     {igsvg}
     <span class="ig__n">Parcours Bijoux</span><span class="ig__h">@parcoursbijoux</span></a>
   </div>
  </div>
 </div>
</footer>
'''

SCRIPT='''
<script>
/* barre : compacte et blanche une fois la page defilee ; fil du telephone apres le hero */
const bar=document.querySelector('.bar'),fil=document.querySelector('.fil'),hero=document.getElementById('top');
function defile(){
  const y=scrollY;
  bar.classList.toggle('on',y>24);
  fil.classList.toggle('on',y>hero.offsetTop+hero.offsetHeight-140);
}
addEventListener('scroll',defile,{passive:true}); defile();

/* apparitions au defilement */
const rv=[...document.querySelectorAll('.split,.affiche figure,.artiste__h,.piece__im,.carnet,.lieu__plan,.lieu__c,.foot')];
rv.forEach(e=>e.classList.add('rv'));
const ro=new IntersectionObserver(es=>es.forEach(e=>{
  if(e.isIntersecting){e.target.classList.add('on');ro.unobserve(e.target);}
}),{rootMargin:'0px 0px -6% 0px',threshold:.04});
rv.forEach(e=>ro.observe(e));

/* visionneuse plein ecran, toutes les pieces a la suite */
const vue=document.getElementById('vue'),vueIm=document.getElementById('vueIm'),
      pieces=[...document.querySelectorAll('.piece__im')];
let cur=-1,lastFocus=null;
function charger(i){ const im=new Image(); im.src=pieces[(i+pieces.length)%pieces.length].dataset.full; }
function montrer(i){
  cur=(i+pieces.length)%pieces.length; const f=pieces[cur];
  vueIm.src=f.dataset.full; vueIm.alt=f.dataset.titre+', '+f.dataset.nom;
  vue.style.background=f.dataset.bg;
  document.getElementById('vueK').textContent=String(cur+1).padStart(2,'0')+' / '+String(pieces.length).padStart(2,'0')+'\\u2002'+f.dataset.nom;
  document.getElementById('vueT').textContent=f.dataset.titre;
  document.getElementById('vueM').textContent=f.dataset.mat;
  document.getElementById('vueC').textContent=f.dataset.cred||'';
  charger(cur+1); charger(cur-1);
}
function ouvrir(f){
  lastFocus=f; montrer(pieces.indexOf(f));
  vue.hidden=false; document.body.style.overflow='hidden';
  vue.querySelector('.vue__x').focus();
}
function fermer(){ vue.hidden=true; vueIm.removeAttribute('src'); document.body.style.overflow='';
  if(lastFocus) lastFocus.focus(); }
pieces.forEach(f=>{
  f.addEventListener('click',()=>{ if(!document.documentElement.classList.contains('edit')) ouvrir(f); });
  f.addEventListener('keydown',e=>{ if(e.key==='Enter'||e.key===' '){e.preventDefault();ouvrir(f);} });
});
vue.addEventListener('click',e=>{ if(!e.target.closest('.vue__c')) fermer(); });
document.getElementById('vuePrec').addEventListener('click',()=>montrer(cur-1));
document.getElementById('vueSuiv').addEventListener('click',()=>montrer(cur+1));
addEventListener('keydown',e=>{
  if(vue.hidden) return;
  if(e.key==='Escape') fermer();
  else if(e.key==='ArrowRight') montrer(cur+1);
  else if(e.key==='ArrowLeft') montrer(cur-1);
});
let tx=null;
vue.addEventListener('touchstart',e=>{ tx=e.changedTouches[0].clientX; },{passive:true});
vue.addEventListener('touchend',e=>{
  if(tx===null) return; const dx=e.changedTouches[0].clientX-tx; tx=null;
  if(Math.abs(dx)>56){ montrer(dx<0?cur+1:cur-1); }
},{passive:true});

/* mode texte : Cmd A rend les textes modifiables, les changements restent dans ce navigateur (localStorage) */
const TXT='main h1,main h2,main h3,main p,main .lbl,main em,.foot p,.foot .lbl';
const cles=()=>[...document.querySelectorAll(TXT)].filter(e=>!e.closest('svg')&&!e.querySelector('p,h1,h2,h3,em,img'));
let mem={}; try{mem=JSON.parse(localStorage.getItem('textes-somogyi')||'{}')}catch(e){}
cles().forEach((e,i)=>{ if(mem[i]!=null) e.innerHTML=mem[i]; });
function modeTexte(on){
  document.documentElement.classList.toggle('edit',on);
  cles().forEach((e,i)=>{ on?e.setAttribute('contenteditable','true'):e.removeAttribute('contenteditable');
    e.oninput=on?()=>{mem[i]=e.innerHTML;localStorage.setItem('textes-somogyi',JSON.stringify(mem));}:null; });
}
addEventListener('keydown',e=>{
  if((e.metaKey||e.ctrlKey)&&!e.shiftKey&&e.key.toLowerCase()==='a'&&vue.hidden){
    e.preventDefault(); modeTexte(!document.documentElement.classList.contains('edit')); }
});
document.addEventListener('click',e=>{ if(document.documentElement.classList.contains('edit')&&e.target.closest('main a')) e.preventDefault(); },true);
document.getElementById('edCopie').addEventListener('click',()=>{
  const out=cles().map((e,i)=>mem[i]!=null?e.innerText.trim():null).filter(Boolean).join('\\n\\n');
  navigator.clipboard.writeText(out||'Aucun texte modifié.'); });
document.getElementById('edRaz').addEventListener('click',()=>{ localStorage.removeItem('textes-somogyi'); location.reload(); });

/* rubrique active dans la barre et dans le fil */
const links=[...document.querySelectorAll('.bar__n a')],fils=[...document.querySelectorAll('.fil__n a')];
const secs=links.map(a=>document.querySelector(a.getAttribute('href')));
const dedans=new Set();
const io=new IntersectionObserver(es=>{
  es.forEach(e=>{
    const i=secs.indexOf(e.target);
    if(i<0)return;
    e.isIntersecting?dedans.add(i):dedans.delete(i);
  });
  const a=dedans.size?Math.max(...dedans):-1;
  links.forEach((l,i)=>l.classList.toggle('on',i===a));fils.forEach((l,i)=>l.classList.toggle('on',i===a));
},{rootMargin:'-45% 0px -50% 0px',threshold:0});
secs.forEach(s=>s&&io.observe(s));
</script>

</body>
</html>
'''

head=HEAD.replace('{jsonld}',JSONLD).replace('{nav}',nav).replace('{desc}',DESC).replace('{site}',SITE)
body=BODY
PLAN=open(S+'images/carte/plan_large.svg').read()+open(S+'images/carte/plan_tel.svg').read()
for k,v in dict(bio=bio,sous=SOUS,dates=DATES,galerie=GALERIE,carte=CARTE,fl=FL,expo=expo,figs=''.join('\n <div class="rang">'+''.join(figs[i] for i in r)+'\n </div>' for r in RANGS),
                igg=IG_GALERIE,igsvg=IGSVG,nom=NOM).items():
    body=body.replace('{%s}'%k,v)
body=body.replace('{n:02d}','%02d'%n)
doc=head+typo(body).replace('{plan}',PLAN)+SCRIPT

open(S+'index.html','w').write(doc)
print('index.html',len(doc),'octets,',n,'pieces')
