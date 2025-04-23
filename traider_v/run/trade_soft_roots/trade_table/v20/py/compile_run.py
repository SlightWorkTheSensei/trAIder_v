import os
import subprocess
import platform

def compile_and_run(ticker):
    """
    Compile the C++ backtesting code and run the executable, passing in the ticker.
    """

    # Dynamically get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define paths for cpp folder and data folder relative to the script directory
    cpp_folder = os.path.join(script_dir, '..', 'cpp')  # Move up one level and then into 'cpp'
    data_folder = os.path.join(script_dir, '..', 'data')  # Move up one level and then into 'data'

    # Ensure the paths are absolute
    cpp_file = os.path.join(cpp_folder, "backtest.cpp")
    executable = os.path.join(cpp_folder, "backtest")

    # Path to Eigen headers (correct MSYS2 path)
    eigen_include_path = "C:/msys64/mingw64/include/eigen3"  # Adjust this to the MSYS2 Eigen path

    # Compile the C++ code with Eigen
    compile_command = f"g++ -I \"{eigen_include_path}\" -o \"{executable}\" \"{cpp_file}\" -std=c++11 -pthread"
    compile_status = os.system(compile_command)

    if compile_status != 0:
        return "Compilation failed"

    # Run the compiled C++ program and pass both the ticker and the data folder as absolute paths
    if platform.system() == "Windows":
        run_command = f"\"{executable}.exe\" {ticker} \"{data_folder}\""
    else:
        run_command = f"\"{executable}\" {ticker} \"{data_folder}\""

    try:
        # Run the executable and capture the output
        result = subprocess.check_output(run_command, shell=True, universal_newlines=True)
        return result
    except subprocess.CalledProcessError as e:
        return f"Error running backtest: {e.output}"

if __name__ == "__main__":
    ticker = "MNQ=F"  # Example ticker
    print(compile_and_run(ticker))
