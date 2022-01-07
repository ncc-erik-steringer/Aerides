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
        # For S3 API interactions, we wanna translate <bucket_name>.s3.amazonaws.com
        # requests to s3.amazonaws.com/<bucket_name> requests.
        if 's3.amazonaws.com' in flow.request.host and 's3.amazonaws.com' != flow.request.host:
            bucket_name = flow.request.host.split('.s3.amazonaws.com')[0]
            flow.request.host = '127.0.0.1'
            flow.request.port = 4566
            flow.request.path = '/{}{}'.format(bucket_name, flow.request.path)

        flow.request.host = '127.0.0.1'
        flow.request.port = 4566
        flow.request.scheme = b'http'

    def response(self, flow: mitmproxy.http.HTTPFlow):
        # For EC2 requests calling DescribeRegions that appear to be trying to filter for
        # "not-opted-in" regions, we manipulate the response from LocalStack that makes it
        # seem that every region isn't opted in
        if 'DescribeRegions' in flow.request.text and 'opt-in-status' in flow.request.text and 'not-opted-in' in flow.request.text:
            flow.response.text = flow.response.text.replace('east', 'fake')
            flow.response.text = flow.response.text.replace('west', 'fake')


addons = [
    Relay()
]


