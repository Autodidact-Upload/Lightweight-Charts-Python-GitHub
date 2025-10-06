"""Test script for Vispy and PyQt5 installation."""
import sys
import vispy
from vispy import app, gloo
import numpy as np

print("=== Vispy and PyQt5 Installation Test ===")
print(f"Python version: {sys.version}")
print(f"Vispy version: {vispy.__version__}")
print(f"Available backends: {vispy.app.backends}")


class SimpleTestCanvas(app.Canvas):
    """Test canvas for displaying a simple triangle."""

    def __init__(self):
        app.Canvas.__init__(
            self,
            title='Vispy Test - Red Triangle',
            size=(400, 400),
            keys='interactive'
        )

        self.program = gloo.Program(
            """
            attribute vec2 position;
            void main() {
                gl_Position = vec4(position, 0.0, 1.0);
            }
            """,
            """
            void main() {
                gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
            }
            """
        )

        self.program['position'] = np.array([
            [0.0, 0.8],
            [-0.8, -0.8],
            [0.8, -0.8]
        ], dtype=np.float32)

        self.show()

    def on_draw(self, event):  # pylint: disable=unused-argument
        """Handle the draw event."""
        gloo.clear(color='black')  # pylint: disable=no-member
        self.program.draw('triangle_strip')


if __name__ == '__main__':
    print("\nStarting visual test...")
    print("You should see a window with a red triangle "
          "on a black background.")
    print("Close the window to end the test.")

    try:
        canvas = SimpleTestCanvas()
        app.run()
        print("✓ Visual test completed successfully!")
    except Exception as e:  # pylint: disable=broad-except
        print(f"✗ Visual test failed: {e}")
