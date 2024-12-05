from flask import Flask, render_template, request, send_file, make_response
import joblib
import numpy as np
import pandas as pd
from xhtml2pdf import pisa
from io import BytesIO

app = Flask(__name__, static_folder='static')

model = joblib.load('./models/iq_prediction_model.pkl')

def interpret_iq(outcome):
    if outcome == 3:
        return "Di Atas Rata-Rata"
    elif outcome == 2:
        return "Rata-Rata"
    elif outcome == 1:
        return "Di Bawah Rata-Rata"
    else:
        return "Tidak Diketahui"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        raw_score = int(request.form['raw_score'])
        predicted_iq = model.predict(np.array([[raw_score]]))[0]

        if 138 >= predicted_iq >= 110:
            outcome = 3
        elif 108 >= predicted_iq >= 90:
            outcome = 2
        elif 89 >= predicted_iq >= 56:
            outcome = 1
        else:
            outcome = 0

        keterangan = interpret_iq(outcome)

        return render_template(
            'result.html',
            raw_score=raw_score,
            predicted_iq=predicted_iq,
            keterangan=keterangan
        )
    except ValueError:
        return "Invalid input. Please enter a numeric value."

# Route baru untuk menghasilkan Excel
@app.route('/download', methods=['POST'])
def download_excel():
    try:
        raw_score = int(request.form['raw_score'])
        predicted_iq = model.predict(np.array([[raw_score]]))[0]

        if 138 >= predicted_iq >= 110:
            outcome = 3
        elif 108 >= predicted_iq >= 90:
            outcome = 2
        elif 89 >= predicted_iq >= 56:
            outcome = 1
        else:
            outcome = 0

        keterangan = interpret_iq(outcome)

        # Membuat DataFrame untuk hasil prediksi
        df = pd.DataFrame({
            'Skor Mentah': [raw_score],
            'Prediksi IQ': [predicted_iq],
            'Keterangan': [keterangan]
        })

        # Simpan ke file Excel
        output_file = "prediksi_iq.xlsx"
        df.to_excel(output_file, index=False)

        # Kirim file ke pengguna
        return send_file(output_file, as_attachment=True)
    except ValueError:
        return "Invalid input. Please enter a numeric value."
    
    # Route untuk mengunduh hasil sebagai PDF
@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    # Ambil data dari form
    raw_score = request.form.get('raw_score')
    predicted_iq = request.form.get('predicted_iq')
    keterangan = request.form.get('keterangan')

    # Render template HTML untuk PDF
    rendered_html = render_template('pdf.html', 
                                     raw_score=raw_score, 
                                     predicted_iq=predicted_iq, 
                                     keterangan=keterangan)

    # Buat PDF dari HTML
    pdf = BytesIO()
    pisa.CreatePDF(BytesIO(rendered_html.encode("UTF-8")), dest=pdf)
    pdf.seek(0)

    # Beri respon sebagai file PDF
    response = make_response(pdf.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=hasil_iq.pdf'
    return response

if __name__ == '__main__':
    app.run(debug=True)
