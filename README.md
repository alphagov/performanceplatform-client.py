## An API client for the [performance platform](https://www.gov.uk/performance)

### Workflow

#### *You're a [developer](http://en.wikipedia.org/wiki/Software_developer)*

<img src="http://f.cl.ly/items/2X3c2m0y0D381P3V2g2j/developer.jpg" alt="developer" stlye="width: 200px" />

#### *You need [data](https://github.com/alphagov/backdrop)*

![](http://f.cl.ly/items/2u262H2a3Q0w000Q3c3f/datacloud.jpg "taste the cloud")

#### *But how do you get there?*

## Well, with the client you can...

#### *Pull data*

![](http://cl.ly/image/2j3I050z1527/pullwhoosh.png)

    from performanceplatform-client import client.DataSet as data_set

    my_data_set = data_set.from_group_and_type(
        'https://www.performance.service.gov.uk/data',
        'gov-uk-content/',
        'top-urls'
    )

    response = my_data_set.get()

#### *and push it*

![](http://i.imgur.com/ksFT6Jx.jpg)

    # Assumes we're still using the same instance as above.
    # Add the correct token for the data-set

    my_data_set.add_token('myImp0rt4nT0k3n')

    my_data_set.post({'foo': 'bar'})



