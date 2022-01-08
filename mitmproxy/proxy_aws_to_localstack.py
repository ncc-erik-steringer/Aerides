"""
The following Python code creates a simple mitmproxy addon. This addon changes the
destination of a proxied HTTP(S) request to http://localhost:4566, the default
endpoint of LocalStack.

This addon should allow users to run dynamic AWS tooling (Scout Suite) against
LocalStack without needing to modify those tools. This requires installing
mitmproxy, configuring the HTTP_PROXY + HTTPS_PROXY + AWS_CA_BUNDLE environment
variables, and running the tool.

For example, with Scout Suite:

```bash
HTTP_PROXY=http://127.0.0.1:8080 \
HTTPS_PROXY=http://127.0.0.1:8080 \
AWS_CA_BUNDLE=~/.mitmproxy/mitmproxy-ca-cert.pem \
scout aws -r us-east-1 --services iam
```
"""

import mitmproxy.http


class Relay:
    def __init__(self):
        pass

    def request(self, flow: mitmproxy.http.HTTPFlow):
        # For S3 API interactions, we wanna translate <bucket_name>.s3.[<region>].amazonaws.com
        # requests to s3.amazonaws.com/<bucket_name> requests.
        # TODO: Currently has the side-effect of making Scout think your buckets are hosted in af-south-1

        host = flow.request.host
        if '.s3.' in host:
            bucket_name = host.split('.')[0]
            flow.request.path = '/{}{}'.format(bucket_name, flow.request.path)

        flow.request.host = '127.0.0.1'
        flow.request.port = 4566
        flow.request.scheme = b'http'

    def response(self, flow: mitmproxy.http.HTTPFlow):
        # For EC2 requests calling DescribeRegions that appear to be trying to filter for
        # "not-opted-in" regions, we manipulate the response from LocalStack to ensure
        # Scout behaves correctly

        if 'DescribeRegions' in flow.request.text and 'opt-in-status' in flow.request.text and 'not-opted-in' in flow.request.text:
            flow.response.text = flow.response.text.replace('east', 'fake')
            flow.response.text = flow.response.text.replace('west', 'fake')


addons = [
    Relay()
]
