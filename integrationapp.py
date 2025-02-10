import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from scipy.integrate import quad
import mpmath
import scipy.special as special
from PIL import Image

# Load the icon image
try:
    icon = Image.open("assets/icon.png")
except:
    icon = "📐"

# Set page configuration
st.set_page_config(
    page_title="Integration Calculator",
    page_icon=icon,
    layout="centered",
    initial_sidebar_state="expanded"
)

# Updated CSS with better contrast
st.markdown("""
    <style>
    body { overflow-x: hidden !important; }
    
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        height: 3em;
        font-weight: bold;
        border-radius: 5px;
    }

    .stTextInput>div>div>input {
        color: #4CAF50;
        font-weight: bold;
    }

    h1, h2, h3 {
        color: #1565C0;
        text-align: center;
    }

    .highlight {
        background-color: #e8f5e9;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 5px solid #4CAF50;
        color: #2E7D32;
        font-size: 1.1em;
        font-weight: 500;
    }

    .result-box {
        background-color: #263238;
        color: #ECEFF1;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 5px solid #FF9800;
        margin: 1rem 0;
        font-size: 1.1em;
        font-weight: bold;
    }

    .function-guide {
        background-color: #1a1a1a;
        color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 5px solid #4CAF50;
        margin: 1rem 0;
    }

    .function-guide h3 {
        color: #4CAF50;
        margin-bottom: 1rem;
    }

    .function-guide ul {
        list-style-type: none;
        padding-left: 0;
    }

    .function-guide li {
        margin-bottom: 0.5rem;
        color: #ffffff;
    }

    .code-text {
        font-family: monospace;
        background-color: #333333;
        padding: 0.2rem 0.4rem;
        border-radius: 3px;
        color: #4CAF50;
    }
    </style>
""", unsafe_allow_html=True)

def try_integration(expr, x):
    """Attempts multiple methods to compute indefinite integral with special functions"""
    try:
        # First attempt: Direct integration with special functions
        result = sp.integrate(expr, x, meijerg=True, risch=True)
        if result.has(sp.Integral):
            # Try converting to special functions
            expr_str = str(expr)
            if 'sin(x**2)' in expr_str:
                S, C = sp.fresnels(x), sp.fresnelc(x)
                result = sp.sqrt(sp.pi/2) * (S + C)
            elif 'exp(-x**2)' in expr_str:
                result = sp.sqrt(sp.pi) * sp.erf(x) / 2
            else:
                # Try simplification before giving up
                simplified = sp.trigsimp(sp.apart(expr))
                result = sp.integrate(simplified, x)
                if result.has(sp.Integral):
                    raise ValueError("Direct integration failed")
        return result
    except:
        try:
            # Second attempt: Using mpmath special functions
            if isinstance(expr, sp.Basic):
                expr_str = str(expr)
                if 'sin(x**2)' in expr_str:
                    return sp.sqrt(sp.pi/2) * (sp.fresnels(x) + sp.fresnelc(x))
                elif 'exp(-x**2)' in expr_str:
                    return sp.sqrt(sp.pi) * sp.erf(x) / 2
            # Try manual integration as last resort
            result = sp.integrate(expr, x, manual=True)
            if result.has(sp.Integral):
                raise ValueError("Manual integration failed")
            return result
        except:
            return None

def evaluate_special_function(expr_str, x_val):
    """Evaluates special functions numerically"""
    try:
        if 'sin(x**2)' in expr_str:
            s, c = special.fresnel(x_val)
            return np.sqrt(np.pi/2) * (s + c)
        elif 'exp(-x**2)' in expr_str:
            return np.sqrt(np.pi) * special.erf(x_val) / 2
        return None
    except:
        return None

def create_plot(x_vals, y_vals, expr_str, lower_limit, upper_limit):
    """Generates a plot for the given function and shaded integral area."""
    plt.style.use('ggplot')
    fig, ax = plt.subplots(figsize=(10, 5))
    
    try:
        # Convert to numpy array and handle special cases
        y_vals = np.asarray(y_vals, dtype=np.float64)
        
        # Handle special functions
        if 'sin(x**2)' in expr_str:
            s, c = special.fresnel(x_vals)
            y_vals = np.sqrt(np.pi/2) * s
        
        # Plot only finite values
        mask = np.isfinite(y_vals)
        ax.plot(x_vals[mask], y_vals[mask], label=f"$f(x) = {expr_str}$", color='#1976D2', linewidth=2.5)
        
        # Only fill between limits where values are finite
        fill_mask = (x_vals >= lower_limit) & (x_vals <= upper_limit) & np.isfinite(y_vals)
        if np.any(fill_mask):
            ax.fill_between(x_vals[fill_mask], y_vals[fill_mask], alpha=0.3, color='#4CAF50', label='Integration Area')
        
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.set_xlabel('x', fontsize=12, fontweight='bold')
        ax.set_ylabel('f(x)', fontsize=12, fontweight='bold')
        ax.set_title(f"Integration of $f(x) = {expr_str}$", fontsize=14, pad=20, fontweight='bold')
        ax.legend(fontsize=10, framealpha=0.9)
        
        plt.tight_layout()
        return fig
    except Exception as e:
        st.error(f"Error creating plot: The function might be undefined in some regions")
        return None
def main():
    st.title('🚀 Advanced Integration Calculator')
    
    st.markdown("""
    <div class='highlight'>
    **Welcome to the Integration Calculator!** This tool computes **definite and indefinite** integrals easily.  
    **Made by Uttaran** 🏆
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📝 Enter Your Function")
        expr_str = st.text_input('Function f(x):', value='x**2', help="Use Python syntax (e.g., x**2 for x²)")
        
        limit_col1, limit_col2 = st.columns(2)
        with limit_col1:
            lower_limit = st.number_input('Lower Limit:', value=0.0, step=0.1, format="%.2f")
        with limit_col2:
            upper_limit = st.number_input('Upper Limit:', value=1.0, step=0.1, format="%.2f")
        
        if st.button('🔢 Calculate Integral', type='primary'):
            try:
                if lower_limit >= upper_limit:
                    st.error("⚠️ Upper limit must be greater than lower limit")
                    return

                x = sp.symbols('x')
                expr = sp.sympify(expr_str)
                
                # Modified lambdify with better function handling
                f = sp.lambdify(x, expr, modules=['numpy', {
                    'sin': np.sin, 
                    'cos': np.cos,
                    'tan': np.tan,
                    'exp': np.exp,
                    'log': np.log,
                    'sqrt': np.sqrt,
                    'pi': np.pi,
                    'erf': special.erf,
                    'fresnels': special.fresnel,
                    'fresnelc': special.fresnel
                }])

                plot_margin = (upper_limit - lower_limit) * 0.2
                x_vals = np.linspace(lower_limit - plot_margin, upper_limit + plot_margin, 1000)
                
                try:
                    y_vals = f(x_vals)
                    if isinstance(y_vals, tuple):  # Handle Fresnel function returns
                        y_vals = y_vals[0]  # Take first component for Fresnel
                    
                    # Convert to float array and handle special cases
                    y_vals = np.asarray(y_vals, dtype=np.float64)
                    
                    # Check for invalid values
                    if np.any(~np.isfinite(y_vals)):
                        st.error("⚠️ Function produces infinite or undefined values")
                        return
                        
                except Exception as calc_error:
                    st.error(f"⚠️ Error calculating function values. Please check your function syntax.")
                    return

                # Try enhanced indefinite integration
                indefinite_result = try_integration(expr, x)
                
                if indefinite_result is not None:
                    latex_integral = sp.latex(indefinite_result)
                    st.markdown(f"""
                    ### Indefinite Integral:
                    $$ \int {sp.latex(expr)} \,dx = {latex_integral} + C $$
                    """, unsafe_allow_html=True)
                else:
                    st.warning("⚠️ Couldn't find a symbolic indefinite integral. "
                              "The function might be too complex for analytical integration.")
                
                try:
                    # Calculate definite integral
                    integral_result, error_estimate = quad(f, lower_limit, upper_limit)
                    
                    # Display plot
                    fig = create_plot(x_vals, y_vals, expr_str, lower_limit, upper_limit)
                    if fig is not None:
                        st.pyplot(fig)

                    # Display Integration Results
                    st.markdown(f"""
                    <div class='result-box'>
                    Integration Results:

                    - 📊 Function: {expr_str}
                    - 📍 Limits: [{lower_limit}, {upper_limit}]
                    - ✨ Definite Integral Result: `{integral_result:.6f}`
                    - 😭 Error Estimate: `{error_estimate:.2e}`
                    </div>
                    """, unsafe_allow_html=True)

                    if abs(error_estimate) > 1e-6:
                        st.warning("⚠️ Note: The error estimate is relatively large.")
                        
                except Exception as int_error:
                    st.error("⚠️ Error computing the definite integral. The function might be too complex or undefined in the given interval.")
                    
            except Exception as e:
                st.error("⚠️ Invalid function syntax. Please check your input.")
                st.info("Make sure to use proper Python syntax (e.g., x**2 for x², sin(x) for sine)")

    with col2:
        st.markdown("""
        <div class='function-guide' style='padding: 1rem; margin-bottom: 0.5rem;'>
        <h3 style='margin-bottom: 0.5rem; font-size: 1.1em;'>💡 Quick Examples:</h3>
        <ul style='list-style-type: none; padding-left: 0; margin-bottom: 0;'>
            <li style='margin-bottom: 5px; font-size: 0.8em;'>
                📊Basic <span class='code-text'>x**2</span>
            </li>
            <li style='margin-bottom: 5px; font-size: 0.8em;'>
                📐Trigonometric<span class='code-text'>sin(x)</span>
            </li>
            <li style='margin-bottom: 5px; font-size: 0.8em;'>
                📈 Expotential <span class='code-text'>exp(-x)</span>
            </li>
            <li style='margin-bottom: 5px; font-size: 0.8em;'>
                🔄Complex <span class='code-text'>sin(x**2)</span>
            </li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

        with st.expander("📚 Function Guide", expanded=False):
            st.markdown("""
            <div class='function-guide'>
            <h3>🔢 Basic Operations</h3>
            • Addition: <span class='code-text'>+</span> (x + 1)<br>
            • Multiplication: <span class='code-text'>*</span> (2*x)<br>
            • Power: <span class='code-text'>**</span> (x**2)<br>
            • Division: <span class='code-text'>/</span> (x/2)<br>

            <h3>🎯 Advanced Functions</h3>
            • Trigonometric: <span class='code-text'>sin(x)</span>, <span class='code-text'>cos(x)</span>, <span class='code-text'>tan(x)</span><br>
            • Inverse Trig: <span class='code-text'>asin(x)</span>, <span class='code-text'>acos(x)</span>, <span class='code-text'>atan(x)</span><br>
            • Exponential: <span class='code-text'>exp(x)</span><br>
            • Logarithmic: <span class='code-text'>log(x)</span>, <span class='code-text'>log10(x)</span><br>
            
            <h3>🎲 Special Functions</h3>
            • Fresnel Integrals: <span class='code-text'>sin(x**2)</span><br>
            • Error Function: <span class='code-text'>exp(-x**2)</span><br>
            • Inverse Functions: <span class='code-text'>1/sqrt(1-x**2)</span><br>
            
            <h3>🎲 Constants</h3>
            • π (pi): <span class='code-text'>pi</span><br>
            • e: <span class='code-text'>e</span><br>
            </div>
            """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
