from setuptools import setup, find_packages
import HTML.Auto

setup(
    name='HTML-Auto',
    version=HTML.Auto.__version__,
    description='Just another HTML tag generator (for Python)',
    author='Jeff Anderson',
    author_email='jeffa@cpan.org',
    url='https://github.com/jeffa/HTML-Auto-python',
    license='MIT',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    long_description="""\
    Just another HTML tag generator.
    --------------------------------

    Generate HTML tags with ease (HTML4, XHTML and HTML5).
"""
)
