from PIL import Image, ImageDraw, ImageFont
import json

# Load data from the JSON file
with open('/Users/prathapselva/Documents/C SQUARE/Pillow/data.json', 'r') as f:
    data = json.load(f)

# Load images
img1 = Image.open('/Users/prathapselva/Documents/C SQUARE/Pillow/mainimg.jpg')
img2 = Image.open('/Users/prathapselva/Documents/C SQUARE/Pillow/up_arrow.jpg')
img3 = Image.open('/Users/prathapselva/Documents/C SQUARE/Pillow/down_arrow.jpg')

# Copy the background image
new = img1.copy()
draw = ImageDraw.Draw(new)
font = ImageFont.truetype('/Users/prathapselva/Documents/C SQUARE/Pillow/impact.ttf', 40)

colors = {
    "C": (199, 21, 133),
    "P": (199, 21, 133)
}

if data[0]["InvoiceTotal"] < data[1]["InvoiceTotal"]:
    img3 = img3.resize((30, 60))
    new.paste(img3, (240, 370))
else:
    img2 = img2.resize((30, 60))
    new.paste(img2, (240, 370))

if data[0]["InvoiceCount"] < data[1]["InvoiceCount"]:
    img3 = img3.resize((30, 60))
    new.paste(img3, (240, 470))
else:
    img2 = img2.resize((30, 60))
    new.paste(img2, (240, 470))

if data[0]["InvoiceAvg"] < data[1]["InvoiceAvg"]:
    img3 = img3.resize((30, 60))
    new.paste(img3, (240, 570))
else:
    img2 = img2.resize((30, 60))
    new.paste(img2, (240, 570))

if data[0]["InvoiceCustomerCount"] < data[1]["InvoiceCustomerCount"]:
    img3 = img3.resize((30, 60))
    new.paste(img3, (240, 670))
else:
    img2 = img2.resize((30, 60))
    new.paste(img2, (240, 670))

if data[0]["InvoiceLineCount"] < data[1]["InvoiceLineCount"]:
    img3 = img3.resize((30, 60))
    new.paste(img3, (240, 770))
else:
    img2 = img2.resize((30, 60))
    new.paste(img2, (240, 770))

if data[0]["NetSale"] < data[1]["NetSale"]:
    img3 = img3.resize((40, 70))
    new.paste(img3, (235, 1110))
else:
    img2 = img2.resize((40, 70))
    new.paste(img2, (235, 1110))

for i in range(2):
    day_type = data[i]['dayType']
    color = colors.get(day_type, (0, 0, 0))
    draw.text((275 if i == 0 else 10, 280), data[i]['DocDt'], font=font, fill=color)
    draw.text((275 if i == 0 else 10, 380), data[i]['InvoiceTotal'], font=font, fill=color)
    draw.text((290 if i == 0 else 50, 480), data[i]['InvoiceCount'], font=font, fill=color)
    draw.text((290 if i == 0 else 50, 580), data[i]['InvoiceAvg'], font=font, fill=color)
    draw.text((290 if i == 0 else 50, 680), data[i]['InvoiceCustomerCount'], font=font, fill=color)
    draw.text((290 if i == 0 else 50, 780), data[i]['InvoiceLineCount'], font=font, fill=color)
    net_sale = float(data[i]['NetSale']) / 100000
    net_sale_formatted = "{:,.3f}".format(net_sale)
    draw.text((300 if i == 0 else 40, 1120), str(net_sale_formatted) + "L", font=font, fill=color)

# Showing the result image
new.show()
