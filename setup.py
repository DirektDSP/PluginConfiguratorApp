from setuptools import setup, find_packages

setup(
    name="plugin_configurator",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "certifi>=2025.1.31",
        "charset-normalizer>=3.4.1",
        "idna>=3.10",
        "PySide6>=6.8.3",
        "PySide6_Addons>=6.8.3",
        "PySide6_Essentials>=6.8.3",
        "requests>=2.32.3",
        "shiboken6>=6.8.3",
        "urllib3>=2.3.0",
        "uuid>=1.30",
    ],
    entry_points={
        "console_scripts": [
            "plugin-configurator=main:main",
        ],
    },
    python_requires=">=3.8",
    author="DirektDSP",
    author_email="info@direktdsp.com",
    description="A GUI application for configuring audio plugin projects",
    keywords="audio, plugin, configuration, juce, cmake",
    url="https://github.com/SeamusMullan/PluginConfiguratorApp",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
