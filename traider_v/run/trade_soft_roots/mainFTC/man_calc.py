from flask import Flask, render_template, request
import math

app = Flask(__name__)

def initialize_ticker_data():
    global ticker_data
    ticker_data = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
  
        contract_size = float(request.form['contract_size'])
        initial_margin = float(request.form['initial_margin'])
        tick_size = float(request.form['tick_size'])
        tick_value = float(request.form['tick_value'])

        # Perform calculations
        buying_power = float(request.form['buying_power'])
        user_risk = float(request.form['risk'])
        entry_price = float(request.form['entry_price'])
        stop_price = float(request.form['stop_price'])

        price_per_contract = contract_size * entry_price
        margin_ratio = round(price_per_contract / initial_margin, 2)
        leveraged_buying_power = round(margin_ratio * buying_power, 2)

        ticks_between = abs(entry_price - stop_price)
        risk_per_contract = (ticks_between / tick_size) * tick_value

        contracts_required = max(1, int(user_risk / risk_per_contract))

        cost_of_contracts = contracts_required * contract_size * entry_price
        actual_risk_exposure = contracts_required * risk_per_contract

        # Calculate leveraged buying power divided by cost of contracts
        leverage_to_cost_ratio = cost_of_contracts / leveraged_buying_power 



        # Prepare data for rendering
        data = {
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

        return render_template('man_calc.html', data=data)

    return render_template('man_calc.html')

if __name__ == '__main__':
    initialize_ticker_data()
    app.run(host='0.0.0.0', port=1001)
