import streamlit as st
import subprocess
import tempfile
import os
import sys
import time
import tracemalloc
import pandas as pd
import plotly.express as px
from pyinstrument import Profiler

# Initialize session state
if 'profiling_result' not in st.session_state:
    st.session_state.profiling_result = None
if 'memory_result' not in st.session_state:
    st.session_state.memory_result = None
if 'flame_svg' not in st.session_state:
    st.session_state.flame_svg = None
if 'code_input' not in st.session_state:
    st.session_state.code_input = '''# Sample Performance Test Script
import time
import random
import math

def fibonacci(n):
    """Recursive fibonacci - CPU intensive"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def matrix_multiply(size):
    """Matrix multiplication - CPU and memory intensive"""
    A = [[random.random() for _ in range(size)] for _ in range(size)]
    B = [[random.random() for _ in range(size)] for _ in range(size)]
    
    result = [[0 for _ in range(size)] for _ in range(size)]
    for i in range(size):
        for j in range(size):
            for k in range(size):
                result[i][j] += A[i][k] * B[k][j]
    return result

def bubble_sort(arr):
    """Inefficient sorting algorithm"""
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def memory_hog():
    """Consumes memory with large data structures"""
    big_list = []
    for i in range(50000):
        big_list.append({
            'id': i,
            'data': [random.random() for _ in range(50)],
            'timestamp': time.time()
        })
    return big_list

def math_operations():
    """Performs various mathematical operations"""
    result = 0
    for i in range(50000):
        result += math.sqrt(i) * math.sin(i) * math.cos(i)
    return result

def io_simulation():
    """Simulates I/O operations"""
    for i in range(50):
        time.sleep(0.01)

def main():
    print("Starting performance test...")
    
    # Test recursive function
    print("Running fibonacci...")
    fib_result = fibonacci(20)
    print(f"Fibonacci result: {fib_result}")
    
    # Test CPU intensive operation
    print("Running matrix multiplication...")
    matrix_result = matrix_multiply(30)
    print(f"Matrix multiplication completed")
    
    # Test sorting
    print("Running bubble sort...")
    unsorted = [random.randint(1, 1000) for _ in range(500)]
    sorted_arr = bubble_sort(unsorted.copy())
    print(f"Sorted array length: {len(sorted_arr)}")
    
    # Test memory usage
    print("Consuming memory...")
    big_data = memory_hog()
    print(f"Created {len(big_data)} objects in memory")
    
    # Test math operations
    print("Running math operations...")
    math_result = math_operations()
    print("Math operations completed")
    
    # Test I/O simulation
    print("Simulating I/O...")
    io_simulation()
    print("I/O simulation completed")
    
    print("Performance test completed!")

if __name__ == "__main__":
    main()
'''

st.set_page_config(page_title="Python Profiler Dashboard", layout="wide")
st.title("🐍 Python Performance Profiler Dashboard")

# Sidebar for options
st.sidebar.header("Profiling Options")

# Code input section
st.sidebar.subheader("Enter Python Code")
code_input = st.sidebar.text_area(
    "Paste your Python code here:",
    value=st.session_state.code_input,
    height=300,
    key="code_editor"
)

# Update session state
st.session_state.code_input = code_input

# Profiling controls
st.sidebar.markdown("---")
run_profiling = st.sidebar.button("Run Profiling")
use_sample = st.sidebar.button("Load Sample Code")

if use_sample:
    st.session_state.code_input = '''# Sample Performance Test Script
import time
import random
import math

def fibonacci(n):
    """Recursive fibonacci - CPU intensive"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def matrix_multiply(size):
    """Matrix multiplication - CPU and memory intensive"""
    A = [[random.random() for _ in range(size)] for _ in range(size)]
    B = [[random.random() for _ in range(size)] for _ in range(size)]
    
    result = [[0 for _ in range(size)] for _ in range(size)]
    for i in range(size):
        for j in range(size):
            for k in range(size):
                result[i][j] += A[i][k] * B[k][j]
    return result

def bubble_sort(arr):
    """Inefficient sorting algorithm"""
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def memory_hog():
    """Consumes memory with large data structures"""
    big_list = []
    for i in range(50000):
        big_list.append({
            'id': i,
            'data': [random.random() for _ in range(50)],
            'timestamp': time.time()
        })
    return big_list

def math_operations():
    """Performs various mathematical operations"""
    result = 0
    for i in range(50000):
        result += math.sqrt(i) * math.sin(i) * math.cos(i)
    return result

def io_simulation():
    """Simulates I/O operations"""
    for i in range(50):
        time.sleep(0.01)

def main():
    print("Starting performance test...")
    
    # Test recursive function
    print("Running fibonacci...")
    fib_result = fibonacci(20)
    print(f"Fibonacci result: {fib_result}")
    
    # Test CPU intensive operation
    print("Running matrix multiplication...")
    matrix_result = matrix_multiply(30)
    print(f"Matrix multiplication completed")
    
    # Test sorting
    print("Running bubble sort...")
    unsorted = [random.randint(1, 1000) for _ in range(500)]
    sorted_arr = bubble_sort(unsorted.copy())
    print(f"Sorted array length: {len(sorted_arr)}")
    
    # Test memory usage
    print("Consuming memory...")
    big_data = memory_hog()
    print(f"Created {len(big_data)} objects in memory")
    
    # Test math operations
    print("Running math operations...")
    math_result = math_operations()
    print("Math operations completed")
    
    # Test I/O simulation
    print("Simulating I/O...")
    io_simulation()
    print("I/O simulation completed")
    
    print("Performance test completed!")

if __name__ == "__main__":
    main()
'''
    st.experimental_rerun()

if run_profiling and st.session_state.code_input:
    with st.spinner("Running performance analysis..."):
        try:
            # Save code to temporary file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(st.session_state.code_input)
                temp_script_path = f.name

            # Run profiling
            profiler = Profiler()
            profiler.start()
            
            # Run script with memory tracing
            tracemalloc.start()
            start_time = time.time()
            
            exec(st.session_state.code_input)
            
            end_time = time.time()
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            profiler.stop()
            
            # Save results
            st.session_state.profiling_result = profiler.output_text(unicode=True, color=False)
            st.session_state.memory_result = {
                "peak_memory": peak / 1024 / 1024,  # MB
                "current_memory": current / 1024 / 1024,  # MB
                "execution_time": end_time - start_time
            }
            
            # Generate flame graph using py-spy
            try:
                subprocess.check_output([
                    sys.executable, "-m", "py_spy", "record", 
                    "-o", "flame.svg", "-f", "flamegraph",
                    "--", sys.executable, temp_script_path
                ], stderr=subprocess.STDOUT, timeout=30)
                with open("flame.svg", "r") as f:
                    st.session_state.flame_svg = f.read()
            except Exception as e:
                st.warning(f"Could not generate flame graph: {str(e)}")
                
        except Exception as e:
            st.error(f"Error running script: {str(e)}")
        finally:
            # Clean up temp file
            if 'temp_script_path' in locals():
                os.unlink(temp_script_path)

# Main dashboard
if st.session_state.profiling_result:
    # Execution summary
    st.header("Execution Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Execution Time", f"{st.session_state.memory_result['execution_time']:.2f}s")
    col2.metric("Peak Memory", f"{st.session_state.memory_result['peak_memory']:.2f} MB")
    col3.metric("Current Memory", f"{st.session_state.memory_result['current_memory']:.2f} MB")
    
    # Function breakdown
    st.header("Function Execution Time")
    # Parse pyinstrument output
    lines = st.session_state.profiling_result.split('\n')
    data = []
    for line in lines[3:]:  # Skip header
        if line.strip() and '%' in line:
            parts = line.split()
            if len(parts) >= 4:
                try:
                    percent = float(parts[0].replace('%', ''))
                    time_val = float(parts[1][:-1])  # Remove 's'
                    function = ' '.join(parts[3:])
                    data.append({
                        'function': function,
                        'time_percent': percent,
                        'time_seconds': time_val
                    })
                except:
                    continue
    
    if data:
        df = pd.DataFrame(data)
        fig = px.bar(
            df.head(15), 
            x='time_percent', 
            y='function', 
            orientation='h',
            labels={'time_percent': 'Time (%)', 'function': 'Function'},
            title='Top Functions by Execution Time'
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Detailed Function Breakdown")
        st.dataframe(df, use_container_width=True)
    
    # Memory usage chart
    st.header("Memory Usage")
    memory_data = pd.DataFrame({
        'Type': ['Peak Memory', 'Current Memory'],
        'MB': [
            st.session_state.memory_result['peak_memory'],
            st.session_state.memory_result['current_memory']
        ]
    })
    fig_mem = px.bar(memory_data, x='Type', y='MB', color='Type')
    st.plotly_chart(fig_mem, use_container_width=True)
    
    # Flame graph
    if st.session_state.flame_svg:
        st.header("Flame Graph")
        st.components.v1.html(st.session_state.flame_svg, height=600, scrolling=True)
    else:
        st.info("Flame graph not available. Install py-spy for flame graph visualization: `pip install py-spy`")

else:
    st.info("Enter Python code in the text area and click 'Run Profiling' to begin analysis")
    st.subheader("Features:")
    st.markdown("""
    - 🔍 Function-level execution time analysis
    - 📊 Memory usage tracking
    - 🔥 Interactive flame graphs
    - 📈 Visual performance breakdown
    """)
    
    st.subheader("Try the sample code:")
    st.code(st.session_state.code_input, language="python")
