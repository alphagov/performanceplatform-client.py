import os
from setuptools import setup, find_packages


def _read(path):
    full_path = os.path.join(os.path.dirname(__file__), path)
    with open(full_path) as f:
        return f.read()


def _get_requirements(path):
    packages = _read(path).splitlines()
    packages = (p for p in packages if not p.startswith('#'))
    packages = (p.strip() for p in packages)

    return packages

if __name__ == '__main__':
    setup(
        name='performanceplatform-client',
        version=_read('VERSION'),
        packages=find_packages(),
        namespace_packages=['performanceplatform'],

        author='GDS Developers',
        author_email='performance@digital.cabinet-office.gov.uk',
        maintainer='Government Digital Service',
        url='https://github.com/alphagov/performanceplatform-client',

        description='A client library for sending data to the Performance '
            'Platform',
        long_description=_read('README.rst'),
        license='MIT',
        keywords='api data performance_platform',

        install_requires=_get_requirements('requirements.txt'),
        tests_require=_get_requirements('requirements_for_tests.txt'),

        test_suite='nose.collector',
    )
