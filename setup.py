from setuptools import setup, find_packages

setup(
    name='kiritan_singing_label_reader',
    version='1.0.0',
    packages=find_packages(),
    url='https://github.com/Hiroshiba/kiritan_singing_label_reader',
    author='Hiroshiba Kazuyuki',
    author_email='hihokaruta@gmail.com',
    license='MIT License',
    install_requires=[
        'numpy',
        'midi @ git+https://github.com/vishnubob/python-midi@feature/python3',
    ],
)
