from distutils.core import setup

setup(
    name='httreplay',
    version='0.1.5',
    author='Aron Griffis, Dave Peck',
    author_email='davepeck+httreplay@gmail.com',
    url='http://github.com/davepeck/httreplay',
    description='A HTTP replay library for testing.',
    license='MIT',
    keywords='test unittest http https replay testing',
    long_description="""\
HTTReplay is a Python HTTP (and HTTPS!) replay library for testing.

The library supports the recording and replay of network requests made via ``httplib``, ``requests >= 1.2.3`` (including ``requests 2.x``), and ``urllib3 >= 0.6``.

Here's a very simple example of how to use it:

::

    import requests
    from httreplay import replay

    with replay('/tmp/recording_file.json'):
        result = requests.get("http://example.com/")
        # ... issue as many requests as you like ...
        # ... repeated requests won't hit the network ...

There's a lot more you can do. Full documentation is available from the `httreplay github page <https://github.com/davepeck/httreplay>`_.
""",
    packages=["httreplay", "httreplay.stubs"],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
    ],
)
