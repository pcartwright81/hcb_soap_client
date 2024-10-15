import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hcb_soap_api-pcartwright81",
    version="0.0.1",
    author="Patrick Cartwright",
    author_email="pcartwright1981@gmail.com",
    description="Soap API for Here Comes the Bus",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pcartwright81/hcb_soapapi",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)