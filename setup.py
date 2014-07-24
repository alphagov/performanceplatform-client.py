import os
import sys

from setuptools import setup, find_packages


def _read(path):
    full_path = os.path.join(os.path.dirname(__file__), path)
    with open(full_path) as f:
        return f.read()


def _recurse_requirements(packages):
    for item in packages:
        if item.startswith('-r '):
            yield list(_get_requirements(item.replace('-r ', '')))
        else:
            yield item


def _get_requirements(path):
    packages = _read(path).splitlines()
    packages = (p for p in packages if not p.startswith('#'))
    packages = (p.strip() for p in packages)
    packages = _recurse_requirements(packages)

    flat_packages = []

    for item in packages:
        if type(item) is list:
            flat_packages = flat_packages + item
        else:
            flat_packages.append(item)

    return list(flat_packages)


def _install_requirements():
    requirements = _get_requirements('requirements.txt')

    if sys.version_info[0] < 3:
        requirements += _get_requirements('requirements_for_python2.txt')

    return requirements


if __name__ == '__main__':
    setup(
        name='performanceplatform-client',
        version=_read('VERSION').strip(),
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

        install_requires=_install_requirements(),
        tests_require=_get_requirements('requirements_for_tests.txt'),

        test_suite='nose.collector',
    )
