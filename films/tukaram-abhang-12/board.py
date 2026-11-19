import cv2, numpy as np, os
from PIL import Image, ImageDraw, ImageFont
ts = [
    ('0.8', '१ हुक: डोळ्यांनी पाहत नाही'),
    ('3.8', '२ हुक: तोंडाने बोलत नाही'),
    ('6.5', '३ हुक: का? (लाल शब्द व रेघ)'),
    ('10.0', '४ आजचा अभंग (स्थिर कार्ड)'),
    ('13.5', '५ अर्थ: तुकोबा म्हणतात'),
    ('15.5', '६ चित्तात हरी (विठ्ठल टिळा)'),
    ('18.5', '७ डोळ्यांना काही दिसत नाही'),
    ('20.5', '८ जिभेवर शब्द उरत नाहीत'),
    ('23.5', '९ सासर-माहेरची दोन घरे'),
    ('25.5', '१० भेदाची भिंत विरघळणे'),
    ('28.0', '११ दोन वाटा एक (वारकरी पताका)'),
    ('32.0', '१२ भांडखोर असल्याचा आळ'),
    ('36.5', '१३ संसाराची बंधने तोडली (स्फोट)'),
    ('41.5', '१४ बंधने गळून पडणे (टेकअवे)'),
    ('44.5', '१५ मनात हरी भरला (शांत मन)'),
    ('49.0', '१६ एकाग्र व्हा (डोळे मिटणे)'),
    ('54.5', '१७ पठण: न देखें न बोलें'),
    ('60.5', '१८ पठण: सासुरें माहेर'),
    ('67.5', '१९ पठण: तुका म्हणे खरी केली मात'),
    ('75.0', '२० शेवट: फॉलो करा व शिक्का'),
]
F = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSerif.ttf', 34, layout_engine=ImageFont.Layout.RAQM)
tw, th = 360, 640; cols = 5; rows = (len(ts) + cols - 1) // cols
sheet = Image.new('RGB', (cols * tw, rows * (th + 46)), (245, 240, 230)); d = ImageDraw.Draw(sheet)
for i, (t, lab) in enumerate(ts):
    im = Image.open(f'out/still_{t}.jpg').resize((tw - 8, th - 8)); x = (i % cols) * tw; y = (i // cols) * (th + 46); sheet.paste(im, (x + 4, y + 4)); d.text((x + 8, y + th), lab, font=F, fill=(20, 20, 20))
os.makedirs('sb', exist_ok=True)
sheet.save('sb/storyboard.jpg', quality=85); print(sheet.size)
