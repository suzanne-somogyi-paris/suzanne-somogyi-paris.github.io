from PIL import Image
import numpy as np, scipy.ndimage as nd, json, os, re

S=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'
R=os.path.expanduser('~/Downloads/RETOUCHES_FINALS_4SEP/')

# (fichier source, matiere, largeur reelle de l objet en cm). Le titre vient du nom du fichier.
# LARGEURS = tailles d affichage reglees a l oeil par Raouf le 19-09 (disque x0.6, bague disque x1.3, bague email x1.4, collier croissant x0.6 puis x1.3, bague verre bleu x1.3), pas des mesures.
# Selection de Raouf du 19-09 : 7 pieces.
OEUVRES = [
 ('FINAL_14_mosaic_disc.jpg','',9.6),
 ('FINAL_08_disc_well_ring.jpg','',5.85),
 ('FINAL_07_silver_crescent_choker.jpg','',10.9),
 ('FINAL_18_red_enamel_ring.jpg','',5.6),
 ('FINAL_09_lozenge_choker.jpg','',14),
 ('FINAL_10_blue_glass_ring_v7.jpg','',6.5),
 ('FINAL_17_lozenge_brooch.jpg','',8),
]
MARGE=0.16          # blanc garde autour de l objet, en part de sa plus grande dimension

def piece(a):
    """masque de l objet par ses contours nets (l ombre, douce, n en a pas) ; les grands vides (interieur d un collier) restent du fond"""
    g=nd.gaussian_filter(a.mean(2),1.2); sat=a.max(2)-a.min(2)
    m=(np.hypot(nd.sobel(g,0),nd.sobel(g,1))>22)|(sat>30)
    k=max(9,int(a.shape[1]/96)|1)
    m=nd.binary_closing(m,np.ones((k,k)))
    plein=nd.binary_fill_holes(m); trous,n=nd.label(plein&~m)
    if n:
        sz=nd.sum(np.ones_like(trous),trous,range(1,n+1)); petits=np.isin(trous,np.where(sz<a.shape[0]*a.shape[1]*0.02)[0]+1)
        m=m|petits
    m=nd.binary_opening(m,np.ones((5,5)))
    lab,n=nd.label(nd.binary_dilation(m,np.ones((31,31))))
    if n>1:
        sz=nd.sum(m,lab,range(1,n+1)); m=m&(lab==1+int(np.argmax(sz)))
    return nd.binary_dilation(m,np.ones((5,5)))

def blanchir(a,m):
    """fond ramene au blanc : le degrade du studio est ajuste par un polynome sur les pixels clairs du fond, l ombre garde sa forme, l objet n est pas touche"""
    h,w,_=a.shape; fond=~nd.binary_dilation(m,np.ones((25,25)))
    yy,xx=np.mgrid[0:h:8,0:w:8]; f=fond[::8,::8]; out=a.copy()
    X=lambda x,y:np.stack([np.ones_like(x),x,y,x*x,y*y,x*y],-1)
    Y,Xg=np.mgrid[0:h,0:w]; full=X(Xg/w,Y/h)
    for c in range(3):
        v=a[::8,::8,c]; ok=f&(v>=np.percentile(v[f],45))            # les pixels clairs : le fond nu, sans l ombre
        coef,*_=np.linalg.lstsq(X(xx[ok]/w,yy[ok]/h),v[ok],rcond=None)
        L=np.clip(full@coef,120,255)
        out[...,c]=np.clip(a[...,c]*(254.0/L),0,255)
    out=np.clip(out*(255.0/242.0),0,255)                             # point blanc : tout ce qui etait presque blanc devient blanc
    ys,xs=np.where(m); t=max(xs.max()-xs.min(),ys.max()-ys.min())
    d=nd.distance_transform_edt(~m)                                   # loin de l objet il n y a plus d ombre : blanc pur
    loin=np.clip((d-0.10*t)/(0.22*t),0,1)[...,None]
    out=out*(1-loin)+255*loin
    k=nd.gaussian_filter(m.astype(np.float32),2.0)[...,None]
    return a*k+out*(1-k)

man=[]
for i,(src,mat,cm) in enumerate(OEUVRES,1):
    title=re.sub(r'^FINAL_\d+_|_v\d+$','',src[:-4]).replace('_',' ').upper()
    im=Image.open(R+src).convert('RGB'); a=np.array(im).astype(np.float32)
    m=piece(a); a=blanchir(a,m)
    ys,xs=np.where(m); x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max()
    g=int(max(x1-x0,y1-y0)*MARGE)
    box=(max(0,x0-g),max(0,y0-g),min(a.shape[1],x1+g),min(a.shape[0],y1+int(g*1.25)))
    c=a[box[1]:box[3],box[0]:box[2]]; hh,ww,_=c.shape                 # le bord du cadre fond dans le blanc de la page
    by=np.minimum(np.arange(hh),np.arange(hh)[::-1])[:,None]/(0.07*hh); bx=np.minimum(np.arange(ww),np.arange(ww)[::-1])[None,:]/(0.07*ww)
    e=np.clip(np.minimum(by,bx),0,1)[...,None]; mc=nd.gaussian_filter(m[box[1]:box[3],box[0]:box[2]].astype(np.float32),2.0)[...,None]
    c=c*np.maximum(e,mc)+255*(1-np.maximum(e,mc))
    im=Image.fromarray(np.clip(c,0,255).astype(np.uint8))
    cadre_cm=cm*(box[2]-box[0])/(x1-x0)                          # largeur reelle couverte par le cadre
    name='suzanne-somogyi_%02d'%i
    im.save(S+'images/oeuvres/'+name+'.jpg','JPEG',quality=90,optimize=True,progressive=True)
    mm=im.copy(); mm.thumbnail((1400,1400), Image.LANCZOS)
    mm.save(S+'images/oeuvres/'+name+'_m.jpg','JPEG',quality=86,optimize=True,progressive=True)
    man.append(dict(titre=title,matiere=mat,src='~/Downloads/RETOUCHES_FINALS_4SEP/'+src,cm=cm,cadre_cm=round(cadre_cm,2),
                    plein='images/oeuvres/'+name+'.jpg',file='images/oeuvres/'+name+'_m.jpg',
                    w=mm.width,h=mm.height,bg='#ffffff'))
    print('%02d %-24s objet %4d px = %4.1f cm, cadre %4dx%-4d = %4.1f cm' % (i,title,x1-x0,cm,im.width,im.height,cadre_cm))
json.dump(dict(oeuvres=man),open(S+'images/manifest.json','w'),ensure_ascii=False,indent=1)
