from flask import Flask, render_template, request, session, redirect, url_for
import csv
import math

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # If user sets buying power and risk
        if 'set_params' in request.form:
            session['buying_power'] = float(request.form['buying_power'])
            session['risk'] = float(request.form['risk'])
            return redirect(url_for('index'))
        
        # If user saves buying power and risk
        if 'save_params' in request.form:
            session['saved_buying_power'] = float(request.form['buying_power'])
            session['saved_risk'] = float(request.form['risk'])
            return redirect(url_for('index'))

        # If user submits trade data
        entry_price = float(request.form['entry_price'])
        stop_price = float(request.form['stop_price'])
        ticker = request.form['ticker'].upper()

        if 'buying_power' in session and 'risk' in session:
            buying_power = session['buying_power']
            user_risk = session['risk']
        elif 'saved_buying_power' in session and 'saved_risk' in session:
            buying_power = session['saved_buying_power']
            user_risk = session['saved_risk']
        else:
            return render_template('index.html', error='Please set your buying power and risk parameters first.')

        # Read the CSV and perform calculations
        with open('tickers.csv', mode='r') as file:
            csv_file = csv.DictReader(file)
            for row in csv_file:
                if row['Ticker'] == ticker:
                    # Extract values from CSV
                    contract_size = float(row['ContractSize'])
                    initial_margin = float(row['InitialMargin'])
                    tick_size = float(row['TickSize'])
                    tick_value = float(row['TickValue'])

                    # Calculations
                    price_per_contract = contract_size * entry_price
                    margin_ratio = round(price_per_contract / initial_margin, 2)
                    leveraged_buying_power = round(margin_ratio * buying_power, 2)

                    ticks_between = abs(entry_price - stop_price)
                    risk_per_contract = (ticks_between / tick_size) * tick_value

                    # Determine the number of contracts
                    contracts_floor = math.floor(buying_power / price_per_contract)
                    contracts_required = max(1, int(user_risk / risk_per_contract))  # Ensure at least one contract is purchased

                    # Calculate the total cost of contracts
                    cost_of_contracts = contracts_required * contract_size * entry_price

                    # Calculate actual risk exposure
                    actual_risk_exposure = contracts_required * risk_per_contract

                    # Calculate leveraged buying power divided by cost of contracts
                    leverage_to_cost_ratio = cost_of_contracts / leveraged_buying_power

                    # Prepare data for rendering
                    data = {
                        'ticker': ticker,
                        'entry': entry_price,
                        'stop': stop_price,
                        'target1': entry_price + (entry_price - stop_price),
                        'target2': entry_price + 2 * (entry_price - stop_price),
                        'contracts_required': contracts_required,
                        'cost_of_contracts': cost_of_contracts,
                        'margin_ratio': margin_ratio,
                        'leveraged_buying_power': leveraged_buying_power,
                        'risk_per_contract': risk_per_contract,
                        'actual_risk_exposure': actual_risk_exposure,
                        'price_per_contract': price_per_contract,
                        'leverage_to_cost_ratio': leverage_to_cost_ratio
                    }

                    return render_template('index.html', data=data)
            # Ticker not found in CSV
            return render_template('index.html', error='Ticker not found')

    # GET request or initial page load
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6001)
