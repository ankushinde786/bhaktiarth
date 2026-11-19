import cv2, numpy as np, os
from PIL import Image, ImageDraw, ImageFont
ts=[('0.5','१ हुक (थंबनेल)'),('6','२ हुक: त्याच्याशिवाय'),('10','३ आजचा अभंग (स्थिर)'),('14','४ प्रेमात बुडलेलं मन'),('18','५ आधीचा धनी: जग'),
('21.5','६ मन तृप्त होत नाही'),('24.5','७ मन देवाकडे वळलं'),('27.5','८ रात्रंदिवस जवळ हवा'),('30.5','९ क्षणभरही करमत नाही'),('34','१० काळजी, बोलणं सोडा'),
('38','११ अनंताच्या रंगात'),('42','१२ जगाकडून मन भरत नाही'),('47','१३ देवाच्या प्रेमात तृप्त'),('52','१४ एकाग्र व्हा'),('55','१५ लाल ठिपका'),
('58','१६ पठण सुरू'),('66','१७ पठण: शब्द ठळक'),('72','१८ पठण: शेवटची ओळ'),('76','१९ शेवट'),('80','२० फॉलो करा'),('82.2','२१ शिक्का')]
F=ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSerif.ttf',34,layout_engine=ImageFont.Layout.RAQM)
tw,th=360,640; cols=5; rows=(len(ts)+cols-1)//cols
sheet=Image.new('RGB',(cols*tw,rows*(th+46)),(245,240,230)); d=ImageDraw.Draw(sheet)
for i,(t,lab) in enumerate(ts):
    im=Image.open(f'out/still_{t}.jpg').resize((tw-8,th-8)); x=(i%cols)*tw; y=(i//cols)*(th+46); sheet.paste(im,(x+4,y+4)); d.text((x+8,y+th),lab,font=F,fill=(20,20,20))
sheet.save('sb/storyboard.jpg',quality=85); print(sheet.size)
