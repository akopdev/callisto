Callisto
========

A zero dependency micro-framework, to perform machine learning experiments without jupyter notebooks.

The main goal of Callisto is to provide a simple task orchestrator to manage the execution of data pipelines and 
effectively manage results. Just like a jupyter notebook allows you to execute only parts of the code, 
Callisto will cache unchanged tasks, and execute only the necessary steps, allowing you to run pipelines multiple 
times with the expected results.

You can also use Callisto to manage task result dependencies, by requesting already computed output of one task 
as input for another.


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

After the first execution of the pipeline, the output will be cached and on second execution you will get results without
executing any of tasks. However, go and change code in a `step2` method, and Callisto will automatically detect the change
and recompute the output for both steps 2 and 3.

## Development setup

In unix-like environment, you can use `make` to run pre-defined commands, like `make init` to install virtual environment, 
`make test` to run tests, and `make lint` to check code style.

See `make help` for more information.

