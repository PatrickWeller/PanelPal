from setuptools import setup, find_packages

setup(
    name="PanelPal",
    version="1.0.0",
    author="Team Jenkins",
    description="A tool for managing genomic panels.",
    url="https://github.com/PatrickWeller/PanelPal",
    packages=find_packages(),
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'PanelPal = PanelPal.main:main',  # Single command for all subcommands
        ],
    },
)
