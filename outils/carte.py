# -*- coding: utf-8 -*-
# Plan du quartier autour de la galerie, dessine depuis les donnees OpenStreetMap (outils/carte/osm.json).
# Sort deux SVG (ecran large, telephone) dans images/carte/, que gen.py colle dans la page.
import json, math, os, heapq, re
S=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'
EL=json.load(open(S+'outils/carte/osm.json'))['elements']

GAL=(48.8873797,2.3472719)             # 9 rue Ramey (Nominatim)
LIGNES={'Château Rouge':'4','Barbès - Rochechouart':'2 · 4','Anvers':'2','Jules Joffrin':'12',
        'Marcadet - Poissonniers':'4 · 12','Lamarck - Caulaincourt':'12','Abbesses':'12'}
KX=111320*math.cos(math.radians(GAL[0])); KY=110540
def metres(lat,lon): return ((lon-GAL[1])*KX, -(lat-GAL[0])*KY)     # x vers l est, y vers le sud

LARG={'primary':18,'primary_link':12,'secondary':15,'tertiary':13,'residential':9.5,'living_street':9.5,
      'unclassified':9.5,'pedestrian':7.5,'footway':2.2,'path':2.2,'steps':3.6}
RANG={'primary':0,'secondary':1,'tertiary':2,'residential':3,'living_street':3,'unclassified':3,'pedestrian':4}

ways=[e for e in EL if e['type']=='way' and 'geometry' in e]
rues=[]
for w in ways:
    t=w.get('tags',{}); h=t.get('highway')
    if h not in LARG or t.get('footway') in ('sidewalk','crossing') or t.get('tunnel') or t.get('indoor'): continue
    rues.append(dict(h=h,nom=t.get('name'),aire=t.get('area')=='yes',ids=w['nodes'],
                     pts=[metres(g['lat'],g['lon']) for g in w['geometry']]))

def anneaux(e):
    if e['type']=='way': return [[metres(g['lat'],g['lon']) for g in e['geometry']]]
    return [[metres(g['lat'],g['lon']) for g in m['geometry']] for m in e.get('members',[]) if m.get('role')=='outer' and 'geometry' in m]
parcs=[r for e in EL if e.get('tags',{}).get('leisure') in ('park','garden') for r in anneaux(e) if len(r)>3]
def aire(r): return abs(sum(r[i][0]*r[i-1][1]-r[i-1][0]*r[i][1] for i in range(len(r))))/2
def centre(r): return (sum(p[0] for p in r)/len(r), sum(p[1] for p in r)/len(r))
REPERES=[(e['tags']['name'],anneaux(e)[0]) for e in EL if e['type']=='way' and
         e.get('tags',{}).get('name') in ('Basilique du Sacré-Cœur','Église Notre-Dame de Clignancourt','Église Saint-Pierre de Montmartre')]
metros=[(e['tags']['name'],metres(e['lat'],e['lon'])) for e in EL if e.get('tags',{}).get('railway')=='station']

# ---- trajet a pied depuis le metro : plus court chemin sur le graphe des rues ----
G={}; P={}
for r in rues:
    if r['aire']: continue
    for a,b,pa,pb in zip(r['ids'],r['ids'][1:],r['pts'],r['pts'][1:]):
        d=math.dist(pa,pb); P[a]=pa; P[b]=pb
        G.setdefault(a,[]).append((b,d)); G.setdefault(b,[]).append((a,d))
def proche(p,filtre=None):
    return min((n for n in P if filtre is None or n in filtre),key=lambda n:math.dist(P[n],p))
def chemin(a,b):
    D={a:0}; prev={}; q=[(0,a)]
    while q:
        d,u=heapq.heappop(q)
        if u==b: break
        if d>D[u]: continue
        for v,w in G[u]:
            if d+w<D.get(v,1e18): D[v]=d+w; prev[v]=u; heapq.heappush(q,(d+w,v))
    out=[b]
    while out[-1]!=a: out.append(prev[out[-1]])
    return [P[n] for n in out[::-1]], D[b]
ramey={n for r in rues if r['nom']=='Rue Ramey' for n in r['ids']}
n_gal=proche((0,0),ramey)
GALP=P[n_gal]                                   # la galerie, posee sur l axe de la rue Ramey
carrossable={n for r in rues if r['h'] in RANG for n in r['ids']}
station=dict(metros)['Château Rouge']
trajet,dist=chemin(proche(station,carrossable),n_gal)
MINUTES=max(1,round(dist/75))                   # 4,5 km/h
print('trajet Chateau Rouge -> galerie : %d m, environ %d min'%(dist,MINUTES))

# ---- chaines de rues du meme nom, pour poser les noms le long de l axe ----
def chaines(nom):
    segs=[r['pts'][:] for r in rues if r['nom']==nom and not r['aire'] and r['h'] in RANG]
    out=[]
    while segs:
        c=segs.pop(0); bouge=True
        while bouge:
            bouge=False
            for s in segs:
                for cand,fin in ((s,True),(s[::-1],True),(s,False),(s[::-1],False)):
                    if fin and math.dist(c[-1],cand[0])<1.5: c=c+cand[1:]
                    elif not fin and math.dist(c[0],cand[-1])<1.5: c=cand[:-1]+c
                    else: continue
                    segs.remove(s); bouge=True; break
                if bouge: break
        out.append(c)
    return out
def longueur(c): return sum(math.dist(a,b) for a,b in zip(c,c[1:]))
def dans(c,box):
    x0,y0,x1,y1=box; best=[]; cur=[]
    for p in c:
        if x0<=p[0]<=x1 and y0<=p[1]<=y1: cur.append(p)
        else:
            if longueur(cur)>longueur(best): best=cur
            cur=[]
    return cur if longueur(cur)>longueur(best) else best
def simplifie(c,tol):
    if len(c)<3: return c
    a,b=c[0],c[-1]; L=math.dist(a,b) or 1e-9
    i,dm=max(((i,abs((b[0]-a[0])*(a[1]-p[1])-(a[0]-p[0])*(b[1]-a[1]))/L) for i,p in enumerate(c[1:-1],1)),key=lambda t:t[1])
    return simplifie(c[:i+1],tol)[:-1]+simplifie(c[i:],tol) if dm>tol else [a,b]
def fenetre(c,L):
    """les troncons de longueur L de la chaine, du plus droit et plus central au moins bon"""
    tot=longueur(c)
    if tot<=L: return [c]
    def point(s):
        for a,b in zip(c,c[1:]):
            d=math.dist(a,b)
            if s<=d: return (a[0]+(b[0]-a[0])*s/d, a[1]+(b[1]-a[1])*s/d) if d else a
            s-=d
        return c[-1]
    def coupe(s0):
        pts=[point(s0)]; s=0
        for a,b in zip(c,c[1:]):
            d=math.dist(a,b)
            if s+d>s0 and s<s0+L and s>=s0: pts.append(a)
            s+=d
        return pts+[point(s0+L)]
    def score(s0):
        w=coupe(s0); return longueur(w)/ (math.dist(w[0],w[-1]) or 1e-9) + abs(s0+L/2-tot/2)/tot*0.08
    return [coupe(s0) for s0 in sorted((i*(tot-L)/24 for i in range(25)),key=score)]

def d_path(pts,ferme=False): return 'M'+' '.join('%.1f %.1f'%p for p in pts)+('Z' if ferme else '')
def echantillons(c,n=7):
    tot=longueur(c); out=[]
    for k in range(n):
        s=tot*k/(n-1)
        for a,b in zip(c,c[1:]):
            d=math.dist(a,b)
            if s<=d or (a,b)==(c[-2],c[-1]): out.append((a[0]+(b[0]-a[0])*min(s,d)/(d or 1),a[1]+(b[1]-a[1])*min(s,d)/(d or 1))); break
            s-=d
    return out

def plan(nom,W,H,ech,cx,cy,corps,noms_mini,metro_gauche=False):
    """W,H en unites SVG ; ech = unites par metre ; (cx,cy) = place de la galerie dans le cadre"""
    def T(p): return (cx+p[0]*ech, cy+p[1]*ech)
    box_m=((-cx)/ech,(-cy)/ech,(W-cx)/ech,(H-cy)/ech)
    marge=60
    def visible(pts): return any(box_m[0]-marge<=p[0]<=box_m[2]+marge and box_m[1]-marge<=p[1]<=box_m[3]+marge for p in pts)
    o=[]
    o.append('<svg class="plan plan--%s" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Plan du quartier : la Galerie Amira Sliman, 9 rue Ramey, à %d minutes à pied du métro Château Rouge">'%(nom,W,H,MINUTES))
    o.append('''<defs>
 <pattern id="h-%s" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(38)"><line x1="0" y1="0" x2="0" y2="5" stroke="#c9c9c4" stroke-width=".7"/></pattern>
 <radialGradient id="g-%s" cx="35%%" cy="35%%" r="75%%"><stop offset="0" stop-color="#ff6a00"/><stop offset=".55" stop-color="#ff2d87"/><stop offset="1" stop-color="#ff00c8"/></radialGradient>
 <clipPath id="c-%s"><rect width="%d" height="%d"/></clipPath>
</defs>'''%(nom,nom,nom,W,H))
    o.append('<g clip-path="url(#c-%s)">'%nom)
    o.append('<rect width="%d" height="%d" fill="#f1f1ee"/>'%(W,H))
    # jardins : trame fine
    for r in sorted(parcs,key=aire,reverse=True):
        if visible(r) and aire(r)>120: o.append('<path d="%s" fill="#f1f1ee"/><path d="%s" fill="url(#h-%s)"/>'%(d_path([T(p) for p in r],1),d_path([T(p) for p in r],1),nom))
    # reperes batis
    for n,r in REPERES:
        if visible(r): o.append('<path d="%s" fill="#d6d6d1"/>'%d_path([T(p) for p in r],1))
    # places pietonnes puis rues, des plus fines aux plus larges, toutes en blanc
    for r in rues:
        if r['aire'] and visible(r['pts']): o.append('<path d="%s" fill="#fff"/>'%d_path([T(p) for p in r['pts']],1))
    for h in sorted(LARG,key=lambda k:LARG[k]):
        if h=='steps': continue
        d=' '.join(d_path([T(p) for p in r['pts']]) for r in rues if r['h']==h and not r['aire'] and visible(r['pts']))
        if d: o.append('<path d="%s" fill="none" stroke="#fff" stroke-width="%.1f" stroke-linecap="round" stroke-linejoin="round"/>'%(d,max(LARG[h]*ech,1.1)))
    d=' '.join(d_path([T(p) for p in r['pts']]) for r in rues if r['h']=='steps' and visible(r['pts']))
    o.append('<path d="%s" fill="none" stroke="#fff" stroke-width="%.1f"/><path d="%s" fill="none" stroke="#b9b9b3" stroke-width="%.1f" stroke-dasharray="1 1.6"/>'%(d,LARG['steps']*ech,d,LARG['steps']*ech))
    # trajet a pied
    o.append('<path d="%s" fill="none" stroke="#111" stroke-width="1.5" stroke-dasharray="0.1 5.2" stroke-linecap="round" stroke-linejoin="round"/>'%d_path([T(p) for p in trajet]))

    # ---- noms de rues, le long de l axe ----
    gx,gy=T(GALP); sx,sy=T(station)
    pris=[(gx,gy)]+[T(p) for p in echantillons(trajet,14)]
    pris+=[(gx-corps*0.62*3.4-i*corps*2.2,gy-corps*0.62*5.6-j*corps) for i in range(7) for j in (0,1.4)]   # etiquette de la galerie
    sens,haut=(-1,-2.6) if metro_gauche else (1,0)
    pris+=[(sx+sens*i*corps*2.2,sy+(j+haut)*corps) for i in range(9) for j in (-0.6,1.1)]                     # etiquette du metro
    pris+=[(22+i*20,H-30) for i in range(int(200*ech/20)+2)]+[(W-30,H-36)]                                    # echelle et nord
    libres=[]
    noms=sorted({r['nom'] for r in rues if r['nom'] and r['h'] in RANG},
                key=lambda n:(n!='Rue Ramey',min(RANG[r['h']] for r in rues if r['nom']==n and r['h'] in RANG)))
    k=0
    for n in noms:
        rang=min(RANG[r['h']] for r in rues if r['nom']==n and r['h'] in RANG)
        taille=corps*(1.18 if rang<=1 else 1.0)
        txt=n.upper(); larg=len(txt)*taille*0.66+len(txt)*taille*0.09
        cands=[dans(c,(box_m[0]+14/ech,box_m[1]+14/ech,box_m[2]-14/ech,box_m[3]-14/ech)) for c in chaines(n)]
        c=max(cands,key=longueur,default=[])
        if longueur(c)*ech<max(larg*1.12,noms_mini): continue
        for c in fenetre(simplifie(c,2.5),larg*1.12/ech):
            c=[T(p) for p in c]
            if c[-1][0]<c[0][0]: c=c[::-1]
            pts=echantillons(c,max(4,int(larg/14)))
            if longueur(c)/(math.dist(c[0],c[-1]) or 1e-9)>1.035: continue          # pas de nom sur un coude
            if not any(math.dist(p,q)<taille*1.6 for p in pts for q in pris): break
        else: continue
        pris+=pts; k+=1
        gras=' font-weight="700"' if n=='Rue Ramey' else ''
        o.append('<path id="r-%s-%d" d="%s" fill="none"/>'%(nom,k,d_path(c)))
        libres.append('<text font-size="%.1f" letter-spacing="%.2f"%s dy=".36em"><textPath href="#r-%s-%d" startOffset="50%%" text-anchor="middle">%s</textPath></text>'%(taille,taille*0.09,gras,nom,k,txt))
    o.append('<g fill="#2b2b2b" font-weight="400">'+''.join(libres)+'</g>')

    # ---- reperes nommes ----
    o.append('<g fill="#757575" font-size="%.1f" letter-spacing="%.2f" text-anchor="middle">'%(corps*0.95,corps*0.13))
    for n,r in REPERES[:1]+[('Square Louise Michel',max((p for p in parcs),key=aire))]:
        x,y=T(centre(r))
        if n.startswith('Basilique'): y+=corps*8.6
        if 20<x<W-20 and 20<y<H-20: o.append('<text x="%.1f" y="%.1f">%s</text>'%(x,y,n.replace('Basilique du ','').upper()))
    o.append('</g>')

    # ---- metro ----
    for n,p in metros:
        x,y=T(p)
        if not(16<x<W-16 and 16<y<H-16): continue
        R=corps*0.95
        o.append('<g><circle cx="%.1f" cy="%.1f" r="%.1f" fill="#111"/><text x="%.1f" y="%.1f" fill="#fff" font-weight="700" font-size="%.1f" text-anchor="middle" dy=".35em">M</text>'%(x,y,R,x,y,corps*1.05))
        if n=='Château Rouge' and metro_gauche:
            o.append('<g text-anchor="end"><text x="%.1f" y="%.1f" font-weight="700" font-size="%.1f" stroke="#f1f1ee" stroke-width="4" paint-order="stroke" stroke-linejoin="round">%s</text><text x="%.1f" y="%.1f" fill="#3b3b3b" font-size="%.1f" stroke="#f1f1ee" stroke-width="4" paint-order="stroke" stroke-linejoin="round">Ligne %s, environ %d min à pied</text></g>'%(x+R,y-R-corps*1.75,corps*1.15,n,x+R,y-R-corps*0.45,corps,LIGNES[n],MINUTES))
        elif n=='Château Rouge':
            o.append('<text x="%.1f" y="%.1f" font-weight="700" font-size="%.1f" stroke="#f1f1ee" stroke-width="4" paint-order="stroke" stroke-linejoin="round">%s</text><text x="%.1f" y="%.1f" fill="#3b3b3b" font-size="%.1f" stroke="#f1f1ee" stroke-width="4" paint-order="stroke" stroke-linejoin="round">Ligne %s, environ %d min à pied</text>'%(x+R+6,y-1,corps*1.15,n,x+R+6,y+corps*1.25,corps,LIGNES[n],MINUTES))
        else:
            o.append('<text x="%.1f" y="%.1f" font-weight="700" font-size="%.1f">%s</text><text x="%.1f" y="%.1f" fill="#757575" font-size="%.1f">Ligne %s</text>'%(x+R+6,y-1,corps*1.15,n,x+R+6,y+corps*1.25,corps,LIGNES.get(n,'')))
        o.append('</g>')

    # ---- la galerie ----
    x,y=T(GALP); R=corps*0.62
    o.append('<g><circle cx="%.1f" cy="%.1f" r="%.1f" fill="url(#g-%s)" opacity=".22"/><circle cx="%.1f" cy="%.1f" r="%.1f" fill="url(#g-%s)"/><circle cx="%.1f" cy="%.1f" r="%.1f" fill="#111"/>'%(x,y,R*4.2,nom,x,y,R*2.1,nom,x,y,R*0.8))
    lx,ly=x-R*3.4,y-R*5.6
    o.append('<path d="M%.1f %.1f L%.1f %.1f" stroke="#111" stroke-width=".8"/>'%(x-R*1.6,y-R*1.6,lx+4,ly+6))
    o.append('<g text-anchor="end"><text x="%.1f" y="%.1f" font-weight="700" font-size="%.1f" stroke="#f1f1ee" stroke-width="4" paint-order="stroke" stroke-linejoin="round">Galerie Amira Sliman</text><text x="%.1f" y="%.1f" font-size="%.1f" fill="#3b3b3b" stroke="#f1f1ee" stroke-width="4" paint-order="stroke" stroke-linejoin="round">9 rue Ramey</text></g></g>'%(lx,ly-corps*0.9,corps*1.5,lx,ly+corps*0.55,corps*1.15))

    # ---- nord et echelle ----
    e100=100*ech; bx,by=22,H-24
    o.append('<g stroke="#111" stroke-width="1" fill="none"><path d="M%.1f %.1f h%.1f M%.1f %.1f v-5 M%.1f %.1f v-5 M%.1f %.1f v-5"/></g>'%(bx,by,e100*2,bx,by,bx+e100,by,bx+e100*2,by))
    o.append('<g font-size="%.1f" fill="#757575" letter-spacing="%.2f"><text x="%.1f" y="%.1f">0</text><text x="%.1f" y="%.1f" text-anchor="middle">100</text><text x="%.1f" y="%.1f" text-anchor="end">200 M</text></g>'%(corps*0.85,corps*0.1,bx,by-9,bx+e100,by-9,bx+e100*2+2,by-9))
    nx,ny=W-30,H-26
    o.append('<g><path d="M%.1f %.1f l-5 13 5 -3.4 5 3.4z" fill="#111"/><text x="%.1f" y="%.1f" font-size="%.1f" fill="#757575" text-anchor="middle" letter-spacing="1">N</text></g>'%(nx,ny-22,nx,ny+4,corps*0.85))
    o.append('</g></svg>')
    svg='\n'.join(o)
    os.makedirs(S+'images/carte',exist_ok=True)
    open(S+'images/carte/plan_%s.svg'%nom,'w').write(svg)
    print('plan_%s.svg %d Ko, %d noms de rues'%(nom,len(svg)//1024,k))

plan('large',760,500,1.0,400,245,9.6,70)
plan('tel',440,560,0.98,235,300,10.6,60,metro_gauche=True)
