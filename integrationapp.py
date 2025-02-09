import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from scipy.integrate import quad

def create_plot(x_vals, y_vals, expr_str, lower_limit, upper_limit):
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Plot function
    ax.plot(x_vals, y_vals, label=f"f(x) = {expr_str}", color='blue')
    
    # Fill integration area
    x_fill = np.linspace(lower_limit, upper_limit, 500)
    y_fill = np.interp(x_fill, x_vals, y_vals)
    ax.fill_between(x_fill, y_fill, alpha=0.3, color='orange')
    
    # Customize plot
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_xlabel('x')
    ax.set_ylabel('f(x)')
    ax.set_title(f"Integration of {expr_str}")
    ax.legend()
    
    return fig

def main():
    st.title('Integration Calculator')
    
    # Create input fields
    expr_str = st.text_input('Function f(x):', value='x**2')
    
    col1, col2 = st.columns(2)
    with col1:
        lower_limit = st.number_input('Lower Limit:', value=0.0)
    with col2:
        upper_limit = st.number_input('Upper Limit:', value=1.0)
    
    if st.button('Calculate Integral'):
        try:
            if lower_limit >= upper_limit:
                st.error("Error: Upper limit must be greater than lower limit")
                return

            # Define symbolic variable and expression
            x = sp.symbols('x')
            try:
                expr = sp.sympify(expr_str)
            except sp.SympifyError:
                st.error("Error: Invalid mathematical expression")
                return

            # Convert to lambda function
            try:
                f = sp.lambdify(x, expr, 'numpy')
                test_val = f(0)
            except Exception as e:
                st.error(f"Error: Unable to evaluate the function: {e}")
                return

            # Calculate plotting range
            plot_margin = (upper_limit - lower_limit) * 0.2
            x_vals = np.linspace(lower_limit - plot_margin, upper_limit + plot_margin, 1000)
            
            try:
                y_vals = f(x_vals)
                if np.any(np.isnan(y_vals)) or np.any(np.isinf(y_vals)):
                    st.error("Error: Function produces invalid values")
                    return
            except Exception as e:
                st.error(f"Error: Unable to evaluate function: {e}")
                return

            # Calculate integral
            try:
                integral_result, error_estimate = quad(f, lower_limit, upper_limit)
            except Exception as e:
                st.error(f"Error: Integration failed: {e}")
                return

            # Create and display plot
            fig = create_plot(x_vals, y_vals, expr_str, lower_limit, upper_limit)
            st.pyplot(fig)
            
            # Display results
            st.success(f"""
            Function: {expr_str}
            Integration limits: [{lower_limit}, {upper_limit}]
            Result = {integral_result:.6f}
            Error estimate: {error_estimate:.2e}
            """)

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()
