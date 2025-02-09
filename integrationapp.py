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
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better visibility & no scrolling issue
st.markdown("""
    <style>
    /* Ensure no extra scrolling on mobile */
    body {
        overflow-x: hidden !important;
    }
    
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        height: 3em;
        font-weight: bold;
    }
    
    .stTextInput>div>div>input {
        color: #1565C0;
        font-weight: bold;
    }
    
    h1 {
        color: #1E88E5;
        text-align: center;
        font-size: 28px;
        font-weight: bold;
    }
    
    .success-box {
        background-color: #ffffff;
        border: 2px solid #4CAF50;
        padding: 15px;
        border-radius: 10px;
        font-size: 16px;
        font-weight: bold;
        color: #2E7D32;
    }

    /* Fix spacing and alignment */
    .result-box ul {
        list-style-type: none;
        padding-left: 0;
    }
    .result-box li {
        margin: 5px 0;
    }
    
    </style>
""", unsafe_allow_html=True)

# Function to create a plot
def create_plot(x_vals, y_vals, expr_str, lower_limit, upper_limit):
    plt.style.use('ggplot')  # Using ggplot style
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot function with improved styling
    ax.plot(x_vals, y_vals, label=f"f(x) = {expr_str}", color='#1976D2', linewidth=2.5)
    
    # Fill integration area
    x_fill = np.linspace(lower_limit, upper_limit, 500)
    y_fill = np.interp(x_fill, x_vals, y_vals)
    ax.fill_between(x_fill, y_fill, alpha=0.3, color='#4CAF50', label='Integration Area')
    
    # Enhanced grid and styling
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_xlabel('x', fontsize=12, fontweight='bold')
    ax.set_ylabel('f(x)', fontsize=12, fontweight='bold')
    ax.set_title(f"Integration of {expr_str}", fontsize=14, pad=20, fontweight='bold')
    ax.legend(fontsize=10, framealpha=0.9)
    plt.tight_layout()
    return fig

# Main app function
def main():
    st.title('🚀 Advanced Integration Calculator')
    
    # Introduction section with visibility fix
    st.markdown("""
    <div class="success-box">
    <h3>Welcome to the Integration Calculator! 🎉</h3>
    This tool computes <strong>definite and indefinite</strong> integrals easily.
    <br><br> <strong>Made by Uttaran</strong>.
    </div>
    """, unsafe_allow_html=True)

    # Create two columns for input
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📝 Enter Your Function")
        expr_str = st.text_input(
            'Function f(x):',
            value='x**2',
            help="Enter a mathematical function using x as the variable"
        )
        
        # Limits in sub-columns
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
                
                # Compute Definite Integral
                integral_result, error_estimate = quad(f, lower_limit, upper_limit)
                
                # Compute Indefinite Integral
                indefinite_integral = sp.integrate(expr, x)
                pretty_integral = sp.latex(indefinite_integral)  # Converts to LaTeX

                # Plot setup
                plot_margin = (upper_limit - lower_limit) * 0.2
                x_vals = np.linspace(lower_limit - plot_margin, upper_limit + plot_margin, 1000)
                y_vals = f(x_vals)
                
                if np.any(np.isnan(y_vals)) or np.any(np.isinf(y_vals)):
                    st.error("⚠️ Function produces invalid values")
                    return
                
                # Display results
                st.pyplot(create_plot(x_vals, y_vals, expr_str, lower_limit, upper_limit))
                
                # Integration Results Box
                st.markdown(f"""
                <div class="success-box result-box">
                    <h3 style="color:#1565C0; text-align:center;">🎉 Integration Results</h3>
                    <ul>
                        <li>📊 <strong>Function:</strong> {expr_str}</li>
                        <li>📍 <strong>Limits:</strong> [{lower_limit}, {upper_limit}]</li>
                        <li>✨ <strong>Definite Integral Result:</strong> {integral_result:.6f}</li>
                        <li>⚠️ <strong>Error Estimate:</strong> {error_estimate:.2e}</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

                # Indefinite Integral
                st.markdown(f"""
                <div class="success-box">
                    <h3 style="color:#1565C0; text-align:center;">✏️ Indefinite Integral</h3>
                    <p style="text-align:center; font-size:18px;">
                        $$ \int {expr_str} \,dx = {pretty_integral} + C $$
                    </p>
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

    # Function guide in an expander
    with st.expander("📚 Function Guide", expanded=False):
        st.markdown("""
        - 📐 Trigonometric: `sin(x)`, `cos(x)`, `tan(x)`
        - 📈 Exponential: `exp(x)`
        - 📉 Logarithmic: `log(x)`, `log10(x)`
        - 🔋 Power: `**` (x**2, not x^2)
        """)

if __name__ == '__main__':
    main()
