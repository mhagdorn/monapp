from setuptools import setup, find_packages

setup(
    name = "monapp",
    packages = find_packages(),
    install_requires = [
        'psutil',
        ],
    entry_points={
        'console_scripts': [
            'monapp = monapp.monapp:main',
            'plotMonapp = monapp.plot:main',
            ],
    },
    author = "Magnus Hagdorn",
    description = "monitor processes",
)
