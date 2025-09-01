import streamlit as st
import subprocess
import tempfile
import os
import sys
import pstats
import io
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pyinstrument import Profiler
import tracemalloc
import time

# Initialize session state
if 'profiling_result' not in st.session_state:
    st.session_state.profiling_result = None
if 'memory_result' not in st.session_state:
    st.session_state.memory_result = None
if 'flame_svg' not in st.session_state:
    st.session_state.flame_svg = None

st.set_page_config(page_title="Python Profiler Dashboard", layout="wide")
st.title("🐍 Python Performance Profiler Dashboard")

# Sidebar for file upload and options
st.sidebar.header("Upload Script")
uploaded_file = st.sidebar.file_uploader("Choose a Python script", type="py")

if uploaded_file:
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(uploaded_file.getvalue().decode('utf-8'))
        temp_script_path = f.name

    st.sidebar.success(f"Saved as: {os.path.basename(temp_script_path)}")
    
    # Profiling options
    st.sidebar.header("Profiling Options")
    run_profiling = st.sidebar.button("Run Profiling")
    
    if run_profiling:
        with st.spinner("Running performance analysis..."):
            try:
                # Run cProfile
                profiler = Profiler()
                profiler.start()
                
                # Run script with memory tracing
                tracemalloc.start()
                start_time = time.time()
                
                exec(open(temp_script_path).read())
                
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
                    flame_output = subprocess.check_output([
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
        
        # Clean up temp file
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
    # Parse pyinstrument output (simplified)
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
    st.info("Upload a Python script and click 'Run Profiling' to begin analysis")
    st.subheader("Features:")
    st.markdown("""
    - 🔍 Function-level execution time analysis
    - 📊 Memory usage tracking
    - 🔥 Interactive flame graphs
    - 📈 Visual performance breakdown
    """)
