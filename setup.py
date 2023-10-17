import setuptools

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="datadoglog",
    version="0.2.0",
    author="Jakub Labath, Ammaar Esmailjee",
    author_email="jakubl@gadventures.com, aesmailjee@gadventures.com",
    description="Logging to datadog",
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
