#  Copyright (c) 2022 Erik Steringer and NCC Group
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

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

        if flow.request.text is not None and 'DescribeRegions' in flow.request.text and 'opt-in-status' in flow.request.text and 'not-opted-in' in flow.request.text:
            flow.response.text = flow.response.text.replace('east', 'fake')
            flow.response.text = flow.response.text.replace('west', 'fake')


addons = [
    Relay()
]
