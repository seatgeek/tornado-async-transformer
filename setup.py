from setuptools import find_packages, setup

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name="tornado-async-transformer",
    version="0.1.7",
    description="libcst transformer and codemod for updating tornado @gen.coroutine syntax to python3.5+ native async/await",
    url="https://github.com/zhammer/tornado-async-transformer",
    packages=find_packages(exclude=["tests", "demo_site"]),
    package_data={"tornado_async_transformer": ["py.typed"]},
    install_requires=["libcst == 0.1.2"],
    author="Zach Hammer",
    author_email="zachary_hammer@alumni.brown.edu",
    license="MIT License",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
