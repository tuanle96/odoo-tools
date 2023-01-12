from setuptools import setup, find_packages

lib_name = 'odoo_tools'


setup(
    name="odoo_tools",
    version="1.0.0",
    author="Justin Le Anh Tuan",
    description="Odoo Toolkits",
    long_description="Scripts",
    long_description_content_type="text/markdown",
    url="https://github.com/tuanle96/odoo_tools",
    packages=find_packages(),
    package_dir={'%s' % lib_name: 'odoo_tools'},
    scripts=['setup/odoo_tools'],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "odoorpc",
        "paramiko",
        "psycopg2",
        "configparser",
        "prettytable",
    ],
    python_requires=">=3.7",
)
