import cv2 as cv
import numpy as np
import cvzone as cvz
import math
from ultralytics import YOLO
import pytesseract
import re
from kafka import KafkaConsumer
import json
import threading

# Global variables
# defualt currency data was updated on 13/05/2025
data_currency = {'AED': 0.0248300639344494, 'AFN': 0.47404459161770895, 'ALL': 0.5973059317274898, 'AMD': 100, 'ANG': 0.01218393056881796, 'AOA': 6.19915120638605, 'ARS': 7.601555512563494, 'AUD': 0.01056726558061543, 'AWG': 0.012168452940663396, 'AZN': 0.011487303664570835, 'BAM': 0.0119099923439803, 'BBD': 0.013623908834048829, 'BDT': 0.819786054349667, 'BGN': 0.011900078886700766, 'BHD': 0.0025480561675350465, 'BIF': 20.07503338487339, 'BMD': 0.006760248933958619, 'BND': 0.008821956475828382, 'BOB': 0.046793984574867, 'BRL': 0.03829025493724949, 'BSD': 0.006747705251800387, 'BTC': 6.485838726504157e-08, 'BTN': 0.573171316259351, 'BWP': 0.09211424139391179, 'BYN': 0.02208229290880378, 'BYR': 132.50092056352148, 'BZD': 0.013553445534758035, 'CAD': 0.0094511755152281, 'CDF': 19.415442452389602, 'CHF': 0.0056909805160655505, 'CLF': 0.00016478692958281165, 'CLP': 6.320768024206719, 'CNY': 0.048925967108934626, 'CNH': 0.04868398034567192, 'COP': 28.604312249436532, 'CRC': 3.426835723996156, 'CUC': 0.006760248933958619, 'CUP': 0.17914665141970457, 'CVE': 0.6714670599231499, 'CZK': 0.15178787835291332, 'DJF': 1.2015815098762788, 'DKK': 0.04531139423683226, 'DOP': 0.3968844603623198, 'DZD': 0.9037848249594759, 'EGP': 0.34144811568290295, 'ERN': 0.10140376438149104, 'ETB': 0.9132195752366624, 'EUR': 0.0060744223526545136, 'FJD': 0.01534037050708312, 'FKP': 0.0050821168659695775, 'GBP': 0.00511747607848438, 'GEL': 0.018556777142813684, 'GGP': 0.0050821168659695775, 'GHS': 0.08737638026593421, 'GIP': 0.0050821168659695775, 'GMD': 0.48335657781914837, 'GNF': 58.43556780939327, 'GTQ': 0.05189746518425086, 'GYD': 1.411751700186777, 'HKD': 0.052679085406056335, 'HNL': 0.17528234689583988, 'HRK': 0.04582436098124688, 'HTG': 0.8825609268965928, 'HUF': 2.464013478851628, 'IDR': 112.53553312626397, 'ILS': 0.02402603516858499, 'IMP': 0.0050821168659695775, 'INR': 0.573834782891975, 'IQD': 8.839007233586146, 'IRR': 284.6065706832207, 'ISK': 0.8908637814614303, 'JEP': 0.0050821168659695775, 'JMD': 1.0724960622101516, 'JOD': 0.004795720000886623, 'JPY': 1.0, 'KES': 0.873763043356548, 'KGS': 0.5911826527958528, 'KHR': 27.002151305271575, 'KMF': 2.9508764137086665, 'KPW': 6.08422732682525, 'KRW': 9.578604972095713, 'KWD': 0.0020776954215019497, 'KYD': 0.005622655413442893, 'KZT': 3.4516828752806834, 'LAK': 145.8871305022277, 'LBP': 604.5619688483333, 'LKR': 2.0166383166288644, 'LRD': 1.3494864291542823, 'LSL': 0.12367573112825647, 'LTL': 0.01996126255823799, 'LVL': 0.004089210011471729, 'LYD': 0.036975901800693864, 'MAD': 0.06295768836205126, 'MDL': 0.11672814093451962, 'MGA': 30.32717940691612, 'MKD': 0.3743915304280542, 'MMK': 14.194444762170482, 'MNT': 24.160841537594962, 'MOP': 0.05415788530454301, 'MRU': 0.2673956771263988, 'MUR': 0.3090096069237043, 'MVR': 0.10413073658500119, 'MWK': 11.70069216281126, 'MXN': 0.13203487129061373, 'MYR': 0.02904867129087738, 'MZN': 0.43197656837743076, 'NAD': 0.12368520115270426, 'NGN': 10.837087959099602, 'NIO': 0.24828206376093961, 'NOK': 0.07040983829966664, 'NPR': 0.9170728850560689, 'NZD': 0.011482869336253396, 'OMR': 0.002602665224485411, 'PAB': 0.006747492647018044, 'PEN': 0.02464794667789447, 'PGK': 0.028005960247510113, 'PHP': 0.3764918469983974, 'PKR': 1.8994365165369742, 'PLN': 0.02577724253747647, 'PYG': 53.91149873997953, 'QAR': 0.02462037487483577, 'RON': 0.0309815707067591, 'RSD': 0.713807387368653, 'RUB': 0.5470146106319266, 'RWF': 9.658936935875609, 'SAR': 0.0253552341933705, 'SBD': 0.056406727575831005, 'SCR': 0.0960634784911113, 'SDG': 4.059567346716674, 'SEK': 0.0661026111955358, 'SGD': 0.008820334605060223, 'SHP': 0.005312495408116353, 'SLE': 0.1537960337873221, 'SLL': 141.75897460519096, 'SOS': 3.856179813884194, 'SRD': 0.24811810295279677, 'STD': 139.92354782444653, 'SVC': 0.059038434613584455, 'SYP': 87.89585519505283, 'SZL': 0.12366327856243353, 'THB': 0.22608291111491544, 'TJS': 0.07030665816158446, 'TMT': 0.023728479589640212, 'TND': 0.02053117093778639, 'TOP': 0.01583321269024339, 'TRY': 0.2620632636873881, 'TTD': 0.045802790707472604, 'TWD': 0.20519729763285166, 'TZS': 18.218875511802732, 'UAH': 0.2802970759425558, 'UGX': 24.69300677327857, 'USD': 0.006760248933958619, 'UYU': 0.28200824679372094, 'UZS': 86.90511673925106, 'VES': 0.6267766052880507, 'VND': 175.57048000091507, 'VUV': 0.8180137991073235, 'WST': 0.01878352318039357, 'XAF': 3.9946437019322985, 'XAG': 0.00020746582103256224, 'XAU': 2.089601289313153e-06, 'XCD': 0.018269912547209576, 'XDR': 0.004900272958420512, 'XOF': 3.994499768494652, 'XPF': 0.7248714009860014, 'YER': 1.6525466982304182, 'ZAR': 0.12366960203610264, 'ZMK': 60.850387754980176, 'ZMW': 0.17765759182186427, 'ZWL': 2.1767980792822303}
stop_consumer = False  # Flag to stop the Kafka consumer loop

#--------------------------------Kafka consumer thread--------------------------------#
# Function to consume messages from Kafka
def consume_messages():
    global data_currency, stop_consumer
    consumer = KafkaConsumer('currency_from_API', bootstrap_servers=['localhost:9092'], auto_offset_reset='latest')
    for message in consumer:
        if stop_consumer:
            break
        # Decode the message value from bytes to string
        message_value = message.value.decode('utf-8')
        
        # Parse the JSON string into a Python dictionary
        data = json.loads(message_value)
        
        # Print the dictionary
        print(data)
        
        # Update the currency data
        data_currency = data

# Start the Kafka consumer in a separate thread
consumer_thread = threading.Thread(target=consume_messages)
consumer_thread.start()

#-------------------------------End of Kafka consumer thread function--------------------------------#

#--------------------------------main setup--------------------------------#
# Path to tesseract
pytesseract.pytesseract.tesseract_cmd = r'E:\scantext\Tesseract-OCR\tesseract.exe'

# Function to extract yen price from OCR text
def extract_yen_price(text):
    for line in text.split('\n'):
        match = re.search(r'[¥￥]?\s?(\d{2,5}(?:,\d{3})?)', line) # Match '¥' or '￥'
        not_tax = re.search(r'税込', line)
        not_gram = re.search(r'g', line) # Match 'g'
        # if in line have '税込' then ignore that line
        if match and not_tax is None and not_gram is None:
            price_str = match.group(1).replace(',', '')
            try:
                price = int(price_str)
                return price
            except ValueError:
                pass
    # If no match found, return None
    print("No price found in the text.")
    return None

# Open camera
cam = cv.VideoCapture(0)
cam.set(cv.CAP_PROP_FRAME_HEIGHT, 360)

# Load YOLO model
model = YOLO('yolo11_custom.pt')

# Input currency you want to use
currency_choice = input("Enter currency: ").upper()
if currency_choice in data_currency.keys():
    pass
else:
    currency_choice = 'AMD'
    print("Invalid currency choice. Defaulting to AMD.")
import time

try:
    while True:
        success, img = cam.read()
        if not success:
            break

        results = model(img, stream=True)

        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                w, h = x2 - x1, y2 - y1
                conf = math.ceil((box.conf[0] * 100)) / 100
                cls = int(box.cls[0])

                if conf >= 0.88:
                    cropped = img[y1:y2, x1:x2]
                    gray = cv.cvtColor(cropped, cv.COLOR_BGR2GRAY)
                    _, thresh = cv.threshold(gray, 127, 255, cv.THRESH_BINARY)
                    
                    ocr_text = pytesseract.image_to_string(thresh, lang='eng+jpn')
                    print("[OCR]:", ocr_text)

                    yen_price = extract_yen_price(ocr_text)
                    if currency_choice in data_currency:
                        EXCHANGE_RATE = data_currency[currency_choice] 
                        symbol = currency_choice
                    else:
                        currency_choice = 'USD'
                        EXCHANGE_RATE = data_currency[currency_choice]
                        print("Invalid currency choice. Defaulting to USD.")
                    
                    if yen_price and currency_choice is not None:
                        currency_price = round(yen_price * EXCHANGE_RATE, 2)
                        label_text = f'YEN{yen_price} / {symbol} {currency_price}'
                    else:
                        label_text = "Price not found"

                    cvz.cornerRect(img, (x1, y1, w, h))
                    cvz.putTextRect(img, label_text, (x1, y1 - 10), scale=1, thickness=1, colorR=(150, 0, 255), colorT=(0, 0, 0), offset=10)

        cv.imshow("YOLO + OCR", img)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
except KeyboardInterrupt:
    print("Exiting program...")

#---------------------------------End of main setup--------------------------------#

# Stop the Kafka consumer thread
stop_consumer = True
consumer_thread.join()

# Release resources
cam.release()
cv.destroyAllWindows()