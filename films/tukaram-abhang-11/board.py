import cv2, numpy as np, os
from PIL import Image, ImageDraw, ImageFont
ts = [
    ('0.8', '१ हुक: पहिली ओळ'),
    ('3.8', '२ हुक: लाल शब्द'),
    ('6.0', '३ हुक: पूर्ण'),
    ('9.2', '४ आजचा अभंग (स्थिर)'),
    ('13.5', '५ तुकोबा म्हणतात'),
    ('15.5', '६ कुळाचार विसरले (तुळशी)'),
    ('19.0', '७ संसाराची नाती (गाठ सुटणे)'),
    ('22.0', '८ लोकांची लाज, भीती'),
    ('24.0', '९ चिंता सांडिली (मुक्त मन)'),
    ('27.5', '१० रातलें अनंता (विठ्ठल टिळा)'),
    ('31.5', '११ साद घालू नका'),
    ('35.5', '१२ कानी बहिरी झाले'),
    ('41.0', '१३ मन हरीत रमलं (टाळ)'),
    ('44.0', '१४ भीती गळून पडते'),
    ('48.5', '१५ एकाग्र व्हा (डोळे मिटणे)'),
    ('53.5', '१६ पठण: विसरले कुळ'),
    ('60.0', '१७ पठण: सांडिला लौकिक'),
    ('67.8', '१८ पठण: तुका म्हणे'),
    ('71.0', '१९ शेवट: भक्ती अर्थ'),
    ('74.8', '२० शिक्का (राम कृष्ण हरी)'),
]
F=ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSerif.ttf',34,layout_engine=ImageFont.Layout.RAQM)
tw,th=360,640; cols=5; rows=(len(ts)+cols-1)//cols
sheet=Image.new('RGB',(cols*tw,rows*(th+46)),(245,240,230)); d=ImageDraw.Draw(sheet)
for i,(t,lab) in enumerate(ts):
    im=Image.open(f'out/still_{t}.jpg').resize((tw-8,th-8)); x=(i%cols)*tw; y=(i//cols)*(th+46); sheet.paste(im,(x+4,y+4)); d.text((x+8,y+th),lab,font=F,fill=(20,20,20))
sheet.save('sb/storyboard.jpg',quality=85); print(sheet.size)
