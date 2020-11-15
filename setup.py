import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="yggdrasilctl",
    version="0.0.1a2",
    author="jorektheglitch",
    author_email="jorektheglitch@yandex.ru",
    description="Wrapper for Yggdrasil Admin API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jorektheglitch/yggdrasilctl",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)