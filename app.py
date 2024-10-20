from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from transformers import MarianMTModel, MarianTokenizer

app = Flask(__name__)

# Load model dan tokenizer untuk penerjemahan bahasa
model_name = 'Helsinki-NLP/opus-mt-id-en'  # Model dari Bahasa Indonesia ke Inggris
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

# Flag untuk memastikan user meminta terjemahan
is_translating = {}

@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    # Ambil nomor telepon pengguna
    user_phone = request.values.get('From', '')
    
    # Ambil pesan yang diterima dari WhatsApp
    incoming_msg = request.values.get('Body', '').strip().lower()

    # Siapkan respon
    resp = MessagingResponse()
    msg = resp.message()

    # Logika untuk merespon pesan
    if incoming_msg == 'halo':
        msg.body('Halo! Apa yang bisa saya bantu?')
        # Reset flag terjemahan jika user mengetik "halo"
        is_translating[user_phone] = False
    
    elif incoming_msg == 'terjemahkan':
        msg.body('Kirim pesan yang ingin diterjemahkan ke bahasa Inggris. Ketik "stop" untuk menghentikan mode terjemahan.')
        # Set flag untuk terjemahan
        is_translating[user_phone] = True
    
    elif incoming_msg == 'stop':
        msg.body('Mode terjemahan dihentikan. Ketik "terjemahkan" untuk memulai lagi.')
        # Reset flag terjemahan ketika pengguna mengetik 'stop'
        is_translating[user_phone] = False
    
    # Jika pengguna sedang dalam mode terjemahan
    elif is_translating.get(user_phone, False):
        try:
            # Proses terjemahan pesan
            inputs = tokenizer(incoming_msg, return_tensors="pt", padding=True)
            translated = model.generate(**inputs)
            translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
        except Exception as e:
            # Jika ada error saat menerjemahkan
            translated_text = "Maaf, saya tidak dapat menerjemahkan pesan ini."

        # Kirim hasil terjemahan atau pesan error
        msg.body(f"Hasil terjemahan: {translated_text}")
    
    else:
        msg.body('Saya tidak mengerti, coba ketik "Halo" atau "Terjemahkan".')

    return str(resp)

if __name__ == '__main__':
    app.run(debug=True)
