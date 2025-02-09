import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from scipy.integrate import quad
from PIL import Image

# Load the icon image
try:
    icon = Image.open("assets/icon.png")
except:
    icon = "📐"  # Fallback emoji if image not found

# Set page configuration
st.set_page_config(
    page_title="Integration Calculator",
    page_icon=icon,
    layout="centered",  # Prevents side scrolling
    initial_sidebar_state="expanded"
)

# Custom CSS to prevent side scrolling and optimize speed
st.markdown("""
    <style>
    .st-emotion-cache-1wrcr25 { overflow: hidden !important; }
    .st-emotion-cache-6qob1r { overflow: hidden !important; }
    .st-emotion-cache-16txtl3 { overflow: hidden !important; }
    .st-emotion-cache-1m0ydde { max-width: 100% !important; }
    h1, h2, h3 { text-align: center; }
    .highlight {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #4CAF50;
        font-size: 1.1em;
    }
    </style>
""", unsafe_allow_html=True)

def create_plot(x_vals, y_vals, expr_str, lower_limit, upper_limit):
    plt.style.use('ggplot')
    fig, ax = plt.subplots(figsize=(10, 5))
    
    ax.plot(x_vals, y_vals, label=f"f(x) = {expr_str}", color='#1976D2', linewidth=2)
    x_fill = np.linspace(lower_limit, upper_limit, 500)
    y_fill = np.interp(x_fill, x_vals, y_vals)
    ax.fill_between(x_fill, y_fill, alpha=0.3, color='#4CAF50', label='Integration Area')

    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_xlabel('x', fontsize=12, fontweight='bold')
    ax.set_ylabel('f(x)', fontsize=12, fontweight='bold')
    ax.set_title(f"Integration of {expr_str}", fontsize=14, pad=10, fontweight='bold')
    ax.legend(fontsize=10, framealpha=0.9)
    plt.tight_layout()
    return fig

def main():
    st.title('Integration Calculator')
    
    st.markdown("""
    <div class='highlight'>
    🚀 **Welcome to the Integration Calculator!** This tool computes **definite and indefinite** integrals easily.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📝 Enter Your Function")
        expr_str = st.text_input(
            'Function f(x):',
            value='x**2',
            help="Enter a function using 'x' (e.g., x**2, sin(x), exp(-x))"
        )
        
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
                f = sp.lambdify(x, expr, 'numpy')

                x_vals = np.linspace(lower_limit, upper_limit, 1000)
                y_vals = f(x_vals)

                if np.any(np.isnan(y_vals)) or np.any(np.isinf(y_vals)):
                    st.error("⚠️ Function produces invalid values")
                    return
                
                # Definite Integral
                integral_result, error_estimate = quad(f, lower_limit, upper_limit)
                
                # Indefinite Integral (Formatted for better readability)
                indefinite_integral = sp.integrate(expr, x)
                integral_latex = sp.latex(indefinite_integral)

                st.pyplot(create_plot(x_vals, y_vals, expr_str, lower_limit, upper_limit))
                
                st.success(f"""
                ### 🎉 Integration Results:
                - 📊 **Function:** `{expr_str}`
                - 📍 **Integration limits:** [{lower_limit}, {upper_limit}]
                - ✨ **Definite Integral:** `{integral_result:.6f}`
                - ⚠️ **Error estimate:** `{error_estimate:.2e}`
                """)

                if abs(error_estimate) > 1e-6:
                    st.warning("⚠️ The error estimate is relatively large.")

                # Display Indefinite Integral
                st.markdown(f"""
                <div class='highlight'>
                ✏️ **Indefinite Integral:**  
                $$ \\int {expr_str} \\,dx = {sp.pretty(indefinite_integral)} + C $$
                </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"⚠️ Error: {str(e)}")
                st.info("Please check your function syntax and try again.")

    with col2:
        st.markdown("### 💡 Quick Examples")
        st.markdown("""
        - 📊 Basic: `x**2`
        - 📐 Trig: `sin(x)`
        - 📈 Exponential: `exp(-x)`
        - 🔄 Complex: `sin(x**2)*exp(-x)`
        """)

    with st.expander("📚 Function Guide", expanded=False):
        st.markdown("""
        ### 🔢 Basic Operations
        - ➕ Addition: `+` (x + 1)
        - ✖️ Multiplication: `*` (2*x)
        - 🔋 Power: `**` (x**2)
        - ➗ Division: `/` (x/2)

        ### 🎯 Advanced Functions
        - 📐 Trigonometric: `sin(x)`, `cos(x)`, `tan(x)`
        - 🔄 Inverse Trig: `asin(x)`, `acos(x)`, `atan(x)`
        - 📈 Exponential: `exp(x)`
        - 📉 Logarithmic: `log(x)`, `log10(x)`
        
        ### 🎲 Constants
        - π (pi): `pi`
        - e: `e`
        """)

if __name__ == '__main__':
    main()
