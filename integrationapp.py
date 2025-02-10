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
    icon = "📐"

# Set page configuration
st.set_page_config(
    page_title="Integration Calculator",
    page_icon=icon,
    layout="centered",  # Prevents horizontal scrolling
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    body { overflow-x: hidden !important; } /* Stops horizontal scrolling */
    
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

    /* General highlight box */
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

    /* Darker background for the integration results */
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

    /* Function Guide Box */
    .function-guide {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #4CAF50;
    }
    </style>
""", unsafe_allow_html=True)

def try_integration(expr, x):
    """Attempts multiple methods to compute indefinite integral"""
    try:
        # First attempt: Direct integration
        result = sp.integrate(expr, x)
        if result.has(sp.Integral):  # Check if integration was successful
            raise ValueError("Direct integration failed")
        return result
    except:
        try:
            # Second attempt: Simplify and integrate
            simplified_expr = sp.trigsimp(sp.apart(expr))
            result = sp.integrate(simplified_expr, x)
            if result.has(sp.Integral):
                raise ValueError("Integration after simplification failed")
            return result
        except:
            try:
                # Third attempt: Manual integration
                result = sp.integrate(expr, x, manual=True)
                if result.has(sp.Integral):
                    raise ValueError("Manual integration failed")
                return result
            except:
                return None

def create_plot(x_vals, y_vals, expr_str, lower_limit, upper_limit):
    """Generates a plot for the given function and shaded integral area."""
    plt.style.use('ggplot')
    fig, ax = plt.subplots(figsize=(10, 5))
    
    ax.plot(x_vals, y_vals, label=f"$f(x) = {expr_str}$", color='#1976D2', linewidth=2.5)
    
    x_fill = np.linspace(lower_limit, upper_limit, 500)
    y_fill = np.interp(x_fill, x_vals, y_vals)
    ax.fill_between(x_fill, y_fill, alpha=0.3, color='#4CAF50', label='Integration Area')
    
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_xlabel('x', fontsize=12, fontweight='bold')
    ax.set_ylabel('f(x)', fontsize=12, fontweight='bold')
    ax.set_title(f"Integration of $f(x) = {expr_str}$", fontsize=14, pad=20, fontweight='bold')
    ax.legend(fontsize=10, framealpha=0.9)
    
    plt.tight_layout()
    return fig

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
                f = sp.lambdify(x, expr, 'numpy')

                plot_margin = (upper_limit - lower_limit) * 0.2
                x_vals = np.linspace(lower_limit - plot_margin, upper_limit + plot_margin, 1000)
                y_vals = f(x_vals)

                if np.any(np.isnan(y_vals)) or np.any(np.isinf(y_vals)):
                    st.error("⚠️ Function produces invalid values")
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
                
                # Still show definite integral (numerical result)
                integral_result, error_estimate = quad(f, lower_limit, upper_limit)
                
                # Display plot
                st.pyplot(create_plot(x_vals, y_vals, expr_str, lower_limit, upper_limit))

                # Display Integration Results in a Dark Box
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
        <div class='function-guide'>
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
        </div>
        """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
