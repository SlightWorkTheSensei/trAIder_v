#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <chrono>
#include <future>  // For thread pooling with async
#include <Eigen/Dense>  // Eigen for vectorized operations

using namespace std;
using namespace std::chrono;
using namespace Eigen;

// Structure to hold individual data points
struct DataPoint {
    string timestamp;
    double open, high, low, close, volume;
};

// Structure to hold backtest results
struct BacktestResult {
    string interval;
    double stop_loss;
    double reward;
    string trade_type;  // "long" or "short"
    string entry_method;
    int total_trades;
    int wins;
    int losses;
    int neutral_trades;
    double gross_profit;
    double gross_loss;
    double net_profit_loss;
    double net_profit_loss_percentage;
    double batting_average;
    double unrealized_gain;  // Added unrealized gain
    double unrealized_loss;  // Added unrealized loss
};

// Function to load data from a CSV file
vector<DataPoint> load_data(const string& filename) {
    vector<DataPoint> data;
    ifstream file(filename);
    string line;

    // Skip the header line
    getline(file, line);

    while (getline(file, line)) {
        DataPoint dp;
        stringstream ss(line);
        string value;

        getline(ss, dp.timestamp, ',');
        getline(ss, value, ',');
        dp.open = stod(value);
        getline(ss, value, ',');
        dp.high = stod(value);
        getline(ss, value, ',');
        dp.low = stod(value);
        getline(ss, value, ',');
        dp.close = stod(value);
        getline(ss, value, ',');
        dp.volume = stod(value);

        data.push_back(dp);
    }

    return data;
}

// Function to aggregate data for a higher timeframe (e.g., 5min, 15min, etc.)
vector<DataPoint> aggregate_data(const vector<DataPoint>& data, int interval_minutes) {
    vector<DataPoint> aggregated_data;
    int interval = interval_minutes;
    int data_size = data.size();

    for (int i = 0; i < data_size; i += interval) {
        DataPoint dp;
        dp.timestamp = data[i].timestamp;
        dp.open = data[i].open;
        dp.high = data[i].high;
        dp.low = data[i].low;
        dp.close = data[i].close;
        dp.volume = data[i].volume;

        for (int j = i; j < i + interval && j < data_size; ++j) {
            dp.high = max(dp.high, data[j].high);
            dp.low = min(dp.low, data[j].low);
            dp.close = data[j].close;
            dp.volume += data[j].volume;
        }

        aggregated_data.push_back(dp);
    }

    return aggregated_data;
}

// Function to convert the data to Eigen matrix for vectorized operations
MatrixXd data_to_matrix(const vector<DataPoint>& data) {
    MatrixXd data_matrix(data.size(), 4);
    for (size_t i = 0; i < data.size(); ++i) {
        data_matrix(i, 0) = data[i].open;
        data_matrix(i, 1) = data[i].high;
        data_matrix(i, 2) = data[i].low;
        data_matrix(i, 3) = data[i].close;
    }
    return data_matrix;
}

// Function to run a single backtest
BacktestResult run_single_backtest(const MatrixXd& data_matrix, double stop_loss, double reward, const string& trade_type, const string& entry_method, const string& interval) {
    BacktestResult result;
    result.interval = interval;
    result.stop_loss = stop_loss;
    result.reward = reward;
    result.trade_type = trade_type;
    result.entry_method = entry_method;

    VectorXd entry_prices;
    if (entry_method == "open") {
        entry_prices = data_matrix.col(0);  // Open prices
    } else if (entry_method == "high") {
        entry_prices = data_matrix.col(1);  // High prices
    } else if (entry_method == "low") {
        entry_prices = data_matrix.col(2);  // Low prices
    } else if (entry_method == "close") {
        entry_prices = data_matrix.col(3);  // Close prices
    }

    VectorXd high_prices = data_matrix.col(1);
    VectorXd low_prices = data_matrix.col(2);

    VectorXd targets, stops;
    if (trade_type == "long") {
        targets = entry_prices.array() + reward * stop_loss;
        stops = entry_prices.array() - stop_loss;
    } else {
        targets = entry_prices.array() - reward * stop_loss;
        stops = entry_prices.array() + stop_loss;
    }

    VectorXd stop_hit = (trade_type == "long") ? (low_prices.array() <= stops.array()).cast<double>() : (high_prices.array() >= stops.array()).cast<double>();
    VectorXd target_hit = (trade_type == "long") ? (high_prices.array() >= targets.array()).cast<double>() : (low_prices.array() <= targets.array()).cast<double>();

    // Add a time-based exit condition (e.g., exit after 50 candles)
    int max_bars_to_hold = 50;
    VectorXd time_exit = (VectorXd::LinSpaced(entry_prices.size(), 0, entry_prices.size() - 1).array() + max_bars_to_hold < entry_prices.size()).cast<double>();

    result.total_trades = entry_prices.size();
    result.wins = (target_hit.array() * time_exit.array()).sum();
    result.losses = (stop_hit.array() * time_exit.array()).sum();
    result.neutral_trades = result.total_trades - result.wins - result.losses;

    result.gross_profit = result.wins * (reward * stop_loss);
    result.gross_loss = result.losses * stop_loss;

    result.net_profit_loss = result.gross_profit - result.gross_loss;
    result.net_profit_loss_percentage = (result.net_profit_loss / result.total_trades) * 100;
    result.batting_average = (static_cast<double>(result.wins) / result.total_trades) * 100;

    // Calculate unrealized gain and loss
    if (trade_type == "long") {
        result.unrealized_gain = (high_prices.array() - entry_prices.array()).maxCoeff();
        result.unrealized_loss = (entry_prices.array() - low_prices.array()).maxCoeff();
    } else {
        result.unrealized_gain = (entry_prices.array() - low_prices.array()).maxCoeff();
        result.unrealized_loss = (high_prices.array() - entry_prices.array()).maxCoeff();
    }

    return result;
}

// Function to run backtests concurrently for different timeframes
vector<BacktestResult> run_backtests_for_all_intervals(const vector<DataPoint>& raw_data, const vector<double>& stop_loss_sizes, const vector<double>& target_sizes, const vector<string>& entry_methods, const vector<string>& trade_types, double batting_average_threshold = 20.0) {
    vector<BacktestResult> all_results;

    // Define the intervals you want to backtest for
    vector<pair<int, string>> intervals = {{1, "1min"}, {5, "5min"}, {15, "15min"}, {30, "30min"}, {60, "60min"}};

    // For each interval, aggregate data and run backtests
    for (const auto& interval : intervals) {
        vector<DataPoint> aggregated_data = (interval.first == 1) ? raw_data : aggregate_data(raw_data, interval.first);
        MatrixXd data_matrix = data_to_matrix(aggregated_data);

        vector<future<BacktestResult>> futures;

        // Run backtests concurrently
        for (const auto& stop_loss : stop_loss_sizes) {
            for (const auto& reward : target_sizes) {
                for (const auto& trade_type : trade_types) {
                    for (const auto& entry_method : entry_methods) {
                        futures.push_back(async(launch::async, run_single_backtest, data_matrix, stop_loss, reward, trade_type, entry_method, interval.second));
                    }
                }
            }
        }

        // Collect all results and exclude results below the batting average threshold
        for (auto& f : futures) {
            BacktestResult result = f.get();
            if (result.batting_average >= batting_average_threshold) {
                all_results.push_back(result);  // Only include if batting average is greater than or equal to threshold
            }
        }
    }

    return all_results;
}

// Function to save the backtest results to a CSV file
void save_results(const vector<BacktestResult>& results, const string& output_filename) {
    ofstream output_file(output_filename);
    output_file << "Interval,Stop Loss,Reward,Trade Type,Entry Method,Total Trades,Wins,Losses,Neutral Trades,Gross Profit,Gross Loss,Net P/L,Net P/L (%),Unrealized Gain,Unrealized Loss,Batting Average" << endl;

    for (const auto& result : results) {
        output_file << result.interval << ","
                    << result.stop_loss << ","
                    << result.reward << ","
                    << result.trade_type << ","
                    << result.entry_method << ","
                    << result.total_trades << ","
                    << result.wins << ","
                    << result.losses << ","
                    << result.neutral_trades << ","
                    << result.gross_profit << ","
                    << result.gross_loss << ","
                    << result.net_profit_loss << ","
                    << result.net_profit_loss_percentage << ","
                    << result.unrealized_gain << ","
                    << result.unrealized_loss << ","
                    << result.batting_average << endl;
    }

    output_file.close();
}

int main(int argc, char* argv[]) {
    if (argc < 3) {
        cout << "Usage: " << argv[0] << " <TICKER> <DATA_DIRECTORY>" << endl;
        return 1;
    }

    string ticker = argv[1];
    string data_directory = argv[2];  
    string filename = data_directory + "/" + ticker + "_1min.csv";
    string output_filename = data_directory + "/backtest_results_" + ticker + ".csv";

    auto start_time = high_resolution_clock::now();

    // Load data
    vector<DataPoint> raw_data = load_data(filename);

    // Backtest parameters
    vector<double> stop_loss_sizes = {0.01, 0.1, 0.25, 0.5, 0.75, 1, 2.5, 5, 10, 25, 50, 100};
    vector<double> target_sizes = {1, 2, 3, 4, 5, 10};
    vector<string> entry_methods = {"open", "high", "low", "close"};
    vector<string> trade_types = {"long", "short"};

    // Set batting average threshold to 20% (or modify as desired)
    double batting_average_threshold = 20.0;

    // Run backtests for all intervals
    vector<BacktestResult> results = run_backtests_for_all_intervals(raw_data, stop_loss_sizes, target_sizes, entry_methods, trade_types, batting_average_threshold);

    // Save results
    save_results(results, output_filename);

    auto end_time = high_resolution_clock::now();
    auto duration = duration_cast<seconds>(end_time - start_time);

    cout << "Backtesting completed in " << duration.count() << " seconds." << endl;

    return 0;
}
