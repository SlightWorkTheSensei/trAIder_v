from flask import jsonify

def get_performance(request, index):
    results = request.args.get('results')
    selected_result = results[int(index)]
    return jsonify(selected_result['account_values'])
