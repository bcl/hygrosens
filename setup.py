# setup.py
from distutils.core import setup
import sys

#windows installer:
# python setup.py bdist_wininst

# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords
if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

setup(
    name="hygrosens",
    description="Hygrosens Device Interface Library",
    version="0.5",
    author="Brian C. Lane",
    author_email="bcl@brianlane.com",
    url="http://www.brianlane.com/software/hygrosens/",
    packages=['hygrosens'],
    license="Python",
    long_description="Hygrosens Device Interface Library",
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Python Software Foundation License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Communications',
        'Topic :: Software Development :: Libraries',
    ],
)
