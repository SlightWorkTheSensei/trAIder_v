from flask import Flask, render_template, request, jsonify, redirect, send_from_directory, session
import csv
import datetime
from datetime import datetime
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from alpha_vantage.timeseries import TimeSeries
import yfinance as yf


app = Flask(__name__)
app.secret_key = 'your_secret_key'

def calculate_average_range(ticker_symbol, period, interval):
     ticker_data = yf.Ticker(ticker_symbol)
     ticker_df = ticker_data.history(period=period, interval=interval)
     ticker_df['Range'] = ticker_df['High'] - ticker_df['Low']
     average_range = ticker_df['Range'].mean().round(2)
     return average_range

def calculate_shares(entry, stop, bp, initial_risk):
    shares = initial_risk / (entry - stop)
    cost = shares * entry

    if cost > bp:
        max_shares = bp // entry
        max_risk = max_shares * (entry - stop)
        shares = max_risk / (entry - stop)
        cost = shares * entry
        return round(max_risk, 8), int(max_shares), round(cost, 8)
    else:
        return round(initial_risk, 8), int(shares), round(cost, 8)

def save_to_csv(data, filename):
    """Save the data to a CSV file without the header row."""
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = [
            "Ticker", "Market Type", "Day/Swing/Core", "Date", "Day Of Week", "Time",
            "Market Bias", "Long/Short", "Volume in Mill", "Avg.Volume", "Pre-M Commitment",
            "$Traded (in mill)", "Resistance", "Support", "Pattern", "Time Updated", "Update Vol",
            "Commitment", "Tickers", "Entry", "Stop", "Entry - Stop", "Risk", "Lot Size", "Cost",
            "Target 1", "Target 2", "Target 3", "Target Hit", "Time/Date Entered",
            "Time/Date Exited", "Time/Date Tar1", "Time/Date Tar2", "Time/Date Tar 3",
            "Avg In", "Avg Out", "P&L"
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        for entry in data:
            writer.writerow(entry)


def calculate_additional_fields(entry):
    if entry['Volume in Mill'] and entry['Avg.Volume']:
        pre_m = float(entry['Volume in Mill']) / float(entry['Avg.Volume']) * 100
        entry['Pre-M Commitment'] = round(pre_m, 2)
    else:
        entry['Pre-M Commitment'] = ""

    # Check for empty strings before converting to float
    if entry['Volume in Mill'] and entry['Resistance']:
        trade_in_mill = float(entry['Volume in Mill']) * float(entry['Resistance'])
        entry['$Traded (in mill)'] = round(trade_in_mill,2)
    else:
        entry['$Traded (in mill)'] = ""

    # Check for empty strings before converting to float
    if entry['Entry'] and entry['Stop']:
        en_min_stop = float(entry['Entry']) - float(entry['Stop'])
        entry['Entry - Stop'] = round(en_min_stop,2)
    else:
        entry['Entry - Stop'] = ""

    # Check for empty strings before converting to float
    if entry['Risk'] and entry['Entry - Stop']:
        lot_s = float(entry['Risk']) / float(entry['Entry - Stop'])
        entry['Lot Size'] = round(lot_s, 2)
    else:
        entry['Lot Size'] = ""

    # Check for empty strings before converting to float
    if entry['Entry'] and entry['Lot Size']:
        cost = float(entry['Entry']) * float(entry['Lot Size'])
        entry['Cost'] = round(cost, 2)
    else:
        entry['Cost'] = ""
    
    for i in range(1, 4):
        # Check for empty strings before converting to float
        if entry['Entry'] and entry['Entry - Stop']:
            entry[f'Target {i}'] = float(entry['Entry']) + float(entry['Entry - Stop']) * i
        else:
            entry[f'Target {i}'] = ""

    # Check for empty strings before converting to float
    if entry['Entry'] and entry['Lot Size']:
        avg_in = float(entry['Entry']) * float(entry['Lot Size'])
        entry['Avg In'] = round(avg_in, 2)
    else:
        entry['Avg In'] = ""

    # Check for empty strings before converting to float
    if entry.get('Target Hit', 0) and entry['Lot Size']:
        entry['Avg Out'] = float(entry['Target Hit']) * float(entry['Lot Size'])
    else:
        entry['Avg Out'] = ""

    # Check for empty strings before converting to float
    if entry['Avg Out'] and entry['Avg In'] and entry['Entry - Stop']:
        entry['P&L'] = abs(float(entry['Avg Out']) - float(entry['Avg In'])) if float(entry['Entry - Stop']) < 0 else (float(entry['Avg Out']) - float(entry['Avg In']))
    else:
        entry['P&L'] = ""
    
    return entry

# Specify the starting row (e.g., row 10)
start_row = 3

def append_to_google_sheets(data):
    # Define the scope and credentials file (JSON key file)
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('auth.json', scope)

    # Authenticate with Google Sheets API
    client = gspread.authorize(creds)

    # Open the desired Google Sheets spreadsheet
    spreadsheet = client.open('----------')

    # Select the worksheet where you want to append data
    worksheet = spreadsheet.worksheet('---------')

    # Specify the path to your CSV file
    csv_file_path = 'form_data.csv'

    # Read data from the CSV file
    data_to_append = []
    with open(csv_file_path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            data_to_append.append(row)

    # Append data to the worksheet starting from the next empty row
    worksheet.insert_rows(data_to_append, start_row, value_input_option='RAW')


@app.route('/', methods=['GET', 'POST'])
def form():
    fields = [
        "Ticker", "Market Type", "Day/Swing/Core", "Day Of Week",
        "Market Bias", "Long/Short", "Volume in Mill", "Avg.Volume", "Resistance",
        "Support", "Pattern", "Entry",
        "Stop", "Risk", "Target Hit"
    ]
    current_time = datetime.now()
    risk, shares, cost, marketbias = None, None, None, None
    if request.method == 'POST':
        if 'bp' in request.form and 'initial_risk' in request.form:
            # Update session with Buying Power and Risk
            session['bp'] = float(request.form['bp'])
            session['initial_risk'] = float(request.form['initial_risk'])
            session['mb'] = str(request.form['mb'])
        elif 'entry' in request.form and 'stop' in request.form:
            # Calculate Shares and Cost
            entry = float(request.form['entry'])
            stop = float(request.form['stop'])
            bp = session.get('bp', 1000)  # Default BP if not set
            initial_risk = session.get('initial_risk', 100)  # Default Risk if not set
            risk, shares, cost = calculate_shares(entry, stop, bp, initial_risk)
    session['username'] = "SWTS TTT"  # Set the default username here
    with open('chat_log.json', 'r') as f:
         chat_log = json.load(f)
    return render_template(
        'form.html',
        fields=fields,
        Risk=risk,
        Shares=shares,
        Cost=cost,
        bp=session.get('bp'),
        initial_risk=session.get('initial_risk'), 
        mb=session.get('mb'),
        chat_log=chat_log,
        current_time=current_time
    )
  


@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    username = session.get('username', "SWTS TTT")  # Use the default username if not set in session
    with open('chat_log.json', 'r+') as f:
        chat_log = json.load(f)
        chat_log.append({'username': username, 'message': message, 'timestamp': timestamp})
        f.seek(0)
        json.dump(chat_log, f)
    return redirect('/')


@app.route('/submit', methods=['POST'])
def submit_form():
    form_data_list = []

    # Create a list of dictionaries with empty fields
    form_data_empty = {
        "Ticker": "", "Market Type": "", "Day/Swing/Core": "", "Date": "",
        "Day Of Week": "", "Time": "", "Market Bias": "", "Long/Short": "",
        "Volume in Mill": "", "Avg.Volume": "", "Pre-M Commitment": "",
        "$Traded (in mill)": "", "Resistance": "", "Support": "", "Pattern": "",
        "Time Updated": "", "Update Vol": "", "Commitment": "", "Tickers": "",
        "Entry": "", "Stop": "", "Entry - Stop": "", "Risk": "", "Lot Size": "",
        "Cost": "", "Target 1": "", "Target 2": "", "Target 3": "", "Target Hit": "",
        "Time/Date Entered": "", "Time/Date Exited": "", "Time/Date Tar1": "",
        "Time/Date Tar2": "", "Time/Date Tar 3": "", "Avg In": "", "Avg Out": "", "P&L": ""
    }


    form_data = form_data_empty.copy()

    for field in request.form:
        value = request.form[field]
        if value:
            form_data[field] = value

    form_data = calculate_additional_fields(form_data)
    form_data_list.append(form_data)

    if form_data_list:
        save_to_csv(form_data_list, 'form_data.csv')
        append_to_google_sheets(form_data_list)

    return jsonify({'status': 'success'})



@app.route('/calculate', methods=['POST'])
def calculate():
    ticker = request.json['ticker']
    ranges = {
        '1-minute': calculate_average_range(ticker, '1d', '1m'),
        '15-minute': calculate_average_range(ticker, '7d', '15m'),
        'Hourly': calculate_average_range(ticker, '30d', '1h'),
        'Daily': calculate_average_range(ticker, '7d', '1d'),
        'Weekly': calculate_average_range(ticker, '4wk', '1wk'),
        'Monthly': calculate_average_range(ticker, '3mo', '1mo')
    }
    return jsonify(ranges=ranges)


@app.route('/data.csv')
def data_csv():
    # Serve the CSV file
    return send_from_directory('static/data', 'data.csv')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 1293)
