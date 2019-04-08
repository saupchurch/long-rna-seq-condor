from setuptools import setup, find_packages
from woldrnaseq.version import get_git_version

setup(
    name='long-rna-seq-condor',
    version=get_git_version(),
    packages=find_packages(),
    package_data={
        'woldrnaseq': ['RELEASE-VERSION'],
        'woldrnaseq.templates': ['*.dagman', '*.html']
    },
    entry_points={
        'console_scripts': [
            'madqc = woldrnaseq.madqc:main',
            'make_dag = woldrnaseq.make_dag:main',
            'makersemcsv = woldrnaseq.makersemcsv:main',
            'make-star-csv = woldrnaseq.makestarcsv:main',
            'qcreport = woldrnaseq.report:main',
        ],
    },
    install_requires=[
        'bokeh>=0.11.3,<1.0',
        'jinja2>=2.8',
        'matplotlib>=3.0',
        'numpy>=1.16',
        'pandas>=0.23',
        'scipy>=1.1',
        'tables>=3.4',
    ],
    author='Diane Trout',
    author_email='diane@caltech.edu',
    description='Implementation of "ENCODE long rna-seq pipeline" using condor',
    zip_safe=False,
    test_suite='woldrnaseq.tests',
)
