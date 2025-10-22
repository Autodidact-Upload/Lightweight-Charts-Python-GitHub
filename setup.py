"""
Setup configuration for Lightweight Charts for Python

Note: This project primarily uses pyproject.toml for configuration.
This setup.py provides backwards compatibility with older pip versions.

For modern installations, all metadata is read from pyproject.toml.
"""

if __name__ == "__main__":
    try:
        from setuptools import setup
        setup()
    except ImportError:
        print("Error: setuptools is required.")
        print("Please install it with: pip install setuptools")
        import sys
        sys.exit(1)
