TamlynScore
===

Django-based archery scoring web application.

## Requirements

The requirements for the project are as follows:
* Python 3
* PIP
* PostgreSQL

On top of these, if you want to modify/recompile the CSS you're going to need:
* Compass

## Installation

Assuming that the requirements have been fulfilled, the installation procedure is as follows:

1. Clone the repository,
2. Run `pip install -r requirements.txt` from the repositories root,
3. Set up the config file (scoring/settings.py),
  * This should include a secret key and the correct database access URI.
4. Run the program using `make run`

The application should then be running, and accessible on `localhost:8001`.

**Note:** It's thoroughly recommended that you use a virtual environment for python to run this project.

## Contributors

* [See all the contributors on GitHub!](https://github.com/mjtamlyn/archery-scoring/graphs/contributors)

## License

The project is covered by an MIT license:
```
The MIT License (MIT)

Copyright (c) 2011-2015 Marc Tamlyn

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```
