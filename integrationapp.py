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

# Custom CSS to improve readability & fix scrolling issues
st.markdown("""
    <style>
    html, body, [class*="st-emotion-cache"] {
        overflow-x: hidden !important; /* Fix side scrolling issue */
        max-width: 100% !important;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        height: 3em;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        color: #4CAF50;
    }
    h1 {
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    h2 {
        color: #1976D2;
        font-weight: bold;
    }
    h3 {
        color: #1565C0;
        font-weight: bold;
    }
    .highlight {
        background-color: #e0f7fa; /* Light blue for visibility */
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 5px solid #0288D1; /* Darker blue border */
        color: #01579B;
        font-size: 1.1em;
        font-weight: bold;
    }
    .success-box {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #4CAF50;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

def create_plot(x_vals, y_vals, expr_str, lower_limit, upper_limit):
    plt.style.use('ggplot')  
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

def main():
    st.title('🚀 **Integration Calculator**')

    # Welcome Message with better visibility
    st.markdown("""
    <div class='highlight'>
    **Welcome to the Integration Calculator!** 🎉  
    This tool computes **definite and indefinite** integrals easily.  
    ✍️ *Made by Uttaran.*
    </div>
    """, unsafe_allow_html=True)

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
                
                plot_margin = (upper_limit - lower_limit) * 0.2
                x_vals = np.linspace(lower_limit - plot_margin, upper_limit + plot_margin, 1000)
                y_vals = f(x_vals)
                
                if np.any(np.isnan(y_vals)) or np.any(np.isinf(y_vals)):
                    st.error("⚠️ Function produces invalid values")
                    return
                
                # **Definite Integral**
                integral_result, error_estimate = quad(f, lower_limit, upper_limit)
                
                # **Indefinite Integral**
                indefinite_integral = sp.integrate(expr, x)
                formatted_integral = sp.latex(indefinite_integral)  # Proper LaTeX formatting

                # Display results
                st.pyplot(create_plot(x_vals, y_vals, expr_str, lower_limit, upper_limit))
                
                st.success(f"""
                ### 🎉 Integration Results:
                - 📊 **Function:** {expr_str}
                - 📍 **Integration limits:** [{lower_limit}, {upper_limit}]
                - ✨ **Definite Integral Result:** {integral_result:.6f}
                - ⚠️ **Error Estimate:** {error_estimate:.2e}
                """)

                # **Indefinite Integral Display**
                st.markdown(f"""
                <div class='highlight'>
                ✏️ **Indefinite Integral:**  
                $$ \int {expr_str} \,dx = {formatted_integral} + C $$
                </div>
                """, unsafe_allow_html=True)

                if abs(error_estimate) > 1e-6:
                    st.warning("⚠️ Note: The error estimate is relatively large.")

            except Exception as e:
                st.error(f"⚠️ Error: {str(e)}")
                st.info("Please check your function syntax and try again.")

    with col2:
        st.markdown("### 💡 Quick Examples")
        st.markdown("""
        - 📊 **Basic:** `x**2`
        - 📐 **Trig:** `sin(x)`
        - 📈 **Exponential:** `exp(-x)`
        - 🔄 **Complex:** `sin(x**2)*exp(-x)`
        """)

if __name__ == '__main__':
    main()
