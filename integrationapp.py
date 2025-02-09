import os
os.environ['KIVY_NO_ARGS'] = '1'

import numpy as np
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.config import Config
import matplotlib
matplotlib.use('Agg')  # Must be before importing plt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image
from io import BytesIO
import sympy as sp
from scipy.integrate import quad

# Configure Kivy
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

class IntegrationCalculator(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10

        # Create the main layout
        self.main_layout = BoxLayout(orientation='vertical', spacing=10)

        # Title
        self.main_layout.add_widget(Label(
            text='Integration Calculator',
            size_hint_y=None,
            height=50,
            font_size=24
        ))

        # Input area
        input_grid = GridLayout(cols=2, size_hint_y=None, height=180, spacing=10)
        
        # Function input
        input_grid.add_widget(Label(text='Function f(x):'))
        self.function_input = TextInput(
            text='x**2',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        input_grid.add_widget(self.function_input)
        
        # Lower limit input
        input_grid.add_widget(Label(text='Lower Limit:'))
        self.lower_input = TextInput(
            text='0',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        input_grid.add_widget(self.lower_input)
        
        # Upper limit input
        input_grid.add_widget(Label(text='Upper Limit:'))
        self.upper_input = TextInput(
            text='1',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        input_grid.add_widget(self.upper_input)
        
        self.main_layout.add_widget(input_grid)
        
        # Calculate button
        self.calc_button = Button(
            text='Calculate Integral',
            size_hint_y=None,
            height=50,
            background_color=(0.3, 0.6, 1, 1)
        )
        self.calc_button.bind(on_press=self.calculate)
        self.main_layout.add_widget(self.calc_button)
        
        # Result label
        self.result_label = Label(
            text='Enter a function and limits, then press Calculate',
            size_hint_y=None,
            height=100,
            text_size=(400, None)
        )
        self.main_layout.add_widget(self.result_label)
        
        # Plot box
        self.plot_box = BoxLayout(size_hint_y=0.7)
        self.plot_image = Image()
        self.plot_box.add_widget(self.plot_image)
        self.main_layout.add_widget(self.plot_box)
        
        self.add_widget(self.main_layout)
        
        # Create initial plot
        self.create_initial_plot()

    def create_initial_plot(self):
        plt.close('all')
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.set_xlabel('x')
        ax.set_ylabel('f(x)')
        ax.set_title('Integration Plot')
        self.update_plot_image(fig)
        plt.close(fig)

    def update_plot_image(self, fig):
        # Save plot to buffer
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        
        # Create Kivy image from buffer
        im = CoreImage(BytesIO(buf.read()), ext='png')
        self.plot_image.texture = im.texture
        buf.close()

    def update_plot(self, x_vals, y_vals, expr_str, lower_limit, upper_limit):
        plt.close('all')
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
        
        # Update image
        self.update_plot_image(fig)
        plt.close(fig)

    def calculate(self, instance):
        try:
            # Get input values
            expr_str = self.function_input.text
            lower_limit = float(self.lower_input.text)
            upper_limit = float(self.upper_input.text)
            
            if lower_limit >= upper_limit:
                self.result_label.text = "Error: Upper limit must be greater than lower limit"
                return

            # Define symbolic variable and expression
            x = sp.symbols('x')
            try:
                expr = sp.sympify(expr_str)
            except sp.SympifyError:
                self.result_label.text = "Error: Invalid mathematical expression"
                return

            # Convert to lambda function
            try:
                f = sp.lambdify(x, expr, 'numpy')
                test_val = f(0)
            except Exception as e:
                self.result_label.text = f"Error: Unable to evaluate the function: {e}"
                return

            # Calculate plotting range
            plot_margin = (upper_limit - lower_limit) * 0.2
            x_vals = np.linspace(lower_limit - plot_margin, upper_limit + plot_margin, 1000)
            
            try:
                y_vals = f(x_vals)
                if np.any(np.isnan(y_vals)) or np.any(np.isinf(y_vals)):
                    self.result_label.text = "Error: Function produces invalid values"
                    return
            except Exception as e:
                self.result_label.text = f"Error: Unable to evaluate function: {e}"
                return

            # Calculate integral
            try:
                integral_result, error_estimate = quad(f, lower_limit, upper_limit)
            except Exception as e:
                self.result_label.text = f"Error: Integration failed: {e}"
                return

            # Update plot
            self.update_plot(x_vals, y_vals, expr_str, lower_limit, upper_limit)
            
            # Display results
            self.result_label.text = (
                f"Function: {expr_str}\n"
                f"Integration limits: [{lower_limit}, {upper_limit}]\n"
                f"Result = {integral_result:.6f}\n"
                f"Error estimate: {error_estimate:.2e}"
            )

        except Exception as e:
            self.result_label.text = f"An unexpected error occurred: {e}"

class IntegrationApp(App):
    def build(self):
        return IntegrationCalculator()

if __name__ == '__main__':
    IntegrationApp().run()
