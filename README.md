## A Python client for the GOV.UK Performance Platform

This repo contains a pip-installable client library for interacting with the [Performance Platform](https://www.gov.uk/performance).

[![PyPI version](https://badge.fury.io/py/performanceplatform-client.svg)](https://pypi.python.org/pypi/performanceplatform-client)
[![Build status](https://travis-ci.org/alphagov/performanceplatform-client.svg?branch=master)](https://travis-ci.org/alphagov/performanceplatform-client)
[![Coverage Status](https://coveralls.io/repos/alphagov/performanceplatform-client/badge.png)](https://coveralls.io/r/alphagov/performanceplatform-client)

### Workflow

#### *You're a [developer](http://en.wikipedia.org/wiki/Software_developer)*

<img src="http://f.cl.ly/items/2X3c2m0y0D381P3V2g2j/developer.jpg" alt="developer" stlye="width: 200px" />

#### *You need [data](https://github.com/alphagov/backdrop)*

![](http://f.cl.ly/items/2u262H2a3Q0w000Q3c3f/datacloud.jpg "taste the cloud")

#### *But how do you get there?*

## Well, with the client you can...

#### *Pull data*

![](http://cl.ly/image/2j3I050z1527/pullwhoosh.png)

```python
from performanceplatform.client import DataSet as data_set

my_data_set = data_set.from_group_and_type(
    'https://www.performance.service.gov.uk/data',
    'gov-uk-content',
    'top-urls'
)

response = my_data_set.get()
```

#### *and push it*

![](http://i.imgur.com/ksFT6Jx.jpg)

```python
# Assumes we're still using the same instance of data_set as above.
# Add the correct token for the data set

my_data_set.set_token('myImp0rt4nT0k3n')

my_data_set.post({'foo': 'bar'})
```
