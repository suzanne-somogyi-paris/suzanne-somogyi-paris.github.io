from PIL import Image
import numpy as np, json, os, re

S=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'
R=os.path.expanduser('~/Downloads/RETOUCHES_FINALS_4SEP/')

# (fichier source, matiere). Le titre affiche vient du nom du fichier : FINAL_01_lapis_ring.jpg -> LAPIS RING.
# Matiere vide = pas encore confirmee, rien n est affiche.
OEUVRES = [
 ('FINAL_01_lapis_ring.jpg',''),
 ('FINAL_02_cream_stone_ring.jpg',''),
 ('FINAL_03_violet_glass_ring.jpg',''),
 ('FINAL_04_agate_ring.jpg',''),
 ('FINAL_05_yellow_stone_ring.jpg',''),
 ('FINAL_06_layered_cuff.jpg',''),
 ('FINAL_07_silver_crescent_choker.jpg',''),
 ('FINAL_08_disc_well_ring.jpg',''),
 ('FINAL_09_lozenge_choker.jpg',''),
 ('FINAL_10_blue_glass_ring_v7.jpg',''),
 ('FINAL_11_amber_ring.jpg',''),
 ('FINAL_12_black_stepped_ring.jpg',''),
 ('FINAL_13_black_dome_ring_v3.jpg',''),
 ('FINAL_14_mosaic_disc.jpg',''),
 ('FINAL_15_sprig_brooch.jpg',''),
 ('FINAL_16_violet_plexi_bracelet.jpg','Plexi violet.'),
 ('FINAL_17_lozenge_brooch.jpg',''),
 ('FINAL_18_red_enamel_ring.jpg',''),
 ('FINAL_19_sprig_pendant_choker.jpg',''),
 ('FINAL_20_bar_choker.jpg',''),
]

def bgcolor(a):
    h,w,_=a.shape; b=max(6,min(h,w)//60)
    ring=np.concatenate([a[:b].reshape(-1,3),a[-b:].reshape(-1,3),a[:,:b].reshape(-1,3),a[:,-b:].reshape(-1,3)])
    return np.median(ring,0)

man=[]
for i,(src,mat) in enumerate(OEUVRES,1):
    title=re.sub(r'^FINAL_\d+_|_v\d+$','',src[:-4]).replace('_',' ').upper()
    im=Image.open(R+src).convert('RGB')             # image entiere, telle quelle
    im.thumbnail((2400,2400), Image.LANCZOS)
    bg=bgcolor(np.array(im).astype(int))
    name='suzanne-somogyi_%02d'%i
    im.save(S+'images/oeuvres/'+name+'.jpg','JPEG',quality=90,optimize=True,progressive=True)
    m=im.copy(); m.thumbnail((1100,1100), Image.LANCZOS)
    m.save(S+'images/oeuvres/'+name+'_m.jpg','JPEG',quality=86,optimize=True,progressive=True)
    man.append(dict(titre=title,matiere=mat,src='~/Downloads/RETOUCHES_FINALS_4SEP/'+src,
                    plein='images/oeuvres/'+name+'.jpg',file='images/oeuvres/'+name+'_m.jpg',
                    w=m.width,h=m.height,bg='#%02x%02x%02x'%tuple(np.round(bg).astype(int))))
    print('%02d %-28s %4dx%-4d bg %s  %s' % (i,title,im.width,im.height,man[-1]['bg'],src))
json.dump(dict(oeuvres=man),open(S+'images/manifest.json','w'),ensure_ascii=False,indent=1)
