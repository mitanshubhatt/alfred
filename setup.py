from setuptools import setup, find_packages

setup(
    name='alfred',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'redis',
        'pytz'
    ],
    author='Mitanshu Bhatt',
    author_email='mitanshubhatt@gofynd.com',
    description='Rules validation for Wayne',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',  # Assuming MIT License, change if different
        'Programming Language :: Python :: 3.10',  # Specify the exact versions you support
        'Programming Language :: Python :: 3.11'
    ],
    python_requires='>=3.10',
)
