Callisto
========

Micro-framework, to perform machine learning experiments without jupyter notebooks.

The main goal of Callisto is to provide a simple task orchestrator to manage the execution of data pipelines and 
effectively manage results. Just like a jupyter notebook allows you to execute only parts of the code, 
Callisto will cache unchanged tasks, and execute only necessary steps, allowing you to run pipelines multiple 
times with the expected results.

You can also use Callisto to manage cross task data, by requesting already computed output of one task 
as an input for another.


## Installation

```bash
pip install git+https://github.com/akopdev/callisto.git
```

## Usage example

Let's create a simple pipeline that will filter data from a list of dictionaries.

```python
from callisto import Callisto

app = Callisto()

@app.task(name="step1")
def get_data():
    return [
        {"id": 1, "name": "John", "last_name": "Doe", "age": 30},
        {"id": 2, "name": "Jane", "last_name": "Doe", "age": 25},
        {"id": 3, "name": "John", "last_name": "Smith", "age": 40},
    ]


@app.task
def step2(step1):
    print("Compute something ....")
    return [item for item in step1 if item["age"] > 30]

@app.task
def final(step2):
    print("Return the result")
    return step2[0]



result = app.run()
print(result)
```

After the first run of the pipeline, the output will be cached and on second execution you will get results without
actual run any of tasks, saving time and computational resources. However, changing code, let's say, in a `step2` 
method will be automatically detected by Callisto, and both steps 2 and 3 will be executed.

## TO-DO

This project (and a concept in general), under heavy development. No public contract is guaranteed at this point.

- [X] Add support for runtime artifacts (settings)
- [X] Add support for multiple run with different settings
- [ ] Terminate pipeline if task raised an exception
- [ ] All stdout should be captured
- [ ] Show task title and description based on the docstring
- [ ] Let task overwrite artifacts
- [ ] Add support for `no_cache` flag in tasks (should help when you write tasks and want to debug)
- [ ] Come up with a better way to handle multiple variables in output


## Development setup

In unix-like environment, you can use `make` to run pre-defined commands, like `make init` to install virtual environment, 
`make test` to run tests, and `make lint` to check code style.

See `make help` for more information.

