import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="datadoglog",
    version="0.0.1",
    author="Jakub Labath",
    author_email="jakubl@gadventures.com",
    description="Logging to datadog log",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gadventures/datadoglog",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
