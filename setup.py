import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bikesanity",
    version="1.0.4",
    author="John Henry",
    author_email="john.henry.split.my.heart@protonmail.com",
    description="BikeSanity cycle touring journal extractor and formatter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JohnHenrySplitMyHeart/bikesanity",
    download_url = 'https://github.com/JohnHenrySplitMyHeart/bikesanity/archive/v_1.0.4.tar.gz',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'beautifulsoup4>=4.8.2',
        'requests>=2.22.0',
        'lxml>=4.5.2',
        'html5lib>=1.1',
        'gpxpy>=1.4.2',
        'Click>=7.0'
    ],
    entry_points={
        'console_scripts': ['bikesanity-run=bikesanity.run:run'],
    },
    include_package_data=True
)
