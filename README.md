# MacLean Lab SNN Infrastructure
An infrastructure for the creation and study of spiking neural networks.

## Installation
These scripts must be run as source,
[ideally](https://www.tensorflow.org/install/pip#2.-create-a-virtual-environment-recommended) in a Python virtual
environment.

To get setup, clone the repository and follow the instructions below:

### Creating a [Python virtual environment](docs.python.org/3/tutorial/venv)
Enter the directory containing `setup.py` and run the following:

#### On Mac/Linux
```bash
python -m venv venv         # create virtual environment
source ./venv/bin/activate  # open virtual environment
pip install -e .            # add this repository to the virtual environment
```

#### On Windows
```bash
python -m venv venv      # create virtual environment
./venv/Scripts/activate  # open virtual environment
pip install -e .         # add this repository to the virtual environment
```

### Closing the virtual environment
When you're done working with the codebase, `deactivate` closes the virtual environment.

## Usage
Meant to be forked.

### Overview
Repository structure is an adaptation of the [Gemy Standard](https://github.com/MrGemy95/Tensorflow-Project-Template):

```
 maclean-snn
│
├── configs
│  └── *.hjson              - Model configs are set and stored in HJSON format
│
├── data
│  └── *.py                 - Data generators and loaders
│
├── loggers
│  ├── *.py                 - Logging API
│  └── callbacks
│     └── *.py              - Callback classes for logging and plotting
│
├── mains
│  └── *.py                 - Each experiment template can have its own main
│
├── models
│  ├── common.py            - Base model and other shared model components
│  ├── *.py                 - Models used in experiments
│  └── neurons
│     ├── base.py           - Neuron model all other neurons inherit from
│     ├── adex.py           - Contains all AdEx neuron variants
│     └── lif.py            - Contains all LIF neuron variants
│
├── trainers
│  └── *.py                 - Model trainers
│
└── utils
   └── *.py                 - Miscellaneous utility functions go here
```

See these subdirectories for further documentation.

### Quick Start

```bash
# once you've built your model, pass filepaths to your main script
# and HJSON configuration file:
python mains/sinusoid_example.py -c configs/sinusoid_example.hjson
```

#### Other configs
See utils/config.py > get_args() for all command line flags that may be passed.

#### Rapid prototyping
While you're adding and removing structural elements, working with the HJSON
configuration could be more trouble than it's worth. It's advised you leave
your HJSON a skeleton and use default values in the class definition while
you're in this phase.

### Troubleshooting
- **Local modules aren't being recognized**
  1. Delete the virtual environment and repeat the installation steps


## Documentation
Documentation for this project is contained in this `README`, a `README` in each subdirectory, and extensive inline
documentation throughout the `.py` scripts.


## Contributing

### Common Modifications
While the script is designed to ultimately provide a model you can control through manipulation of just one HJSON
file, there are many changes you will often find yourself wanting to make in the Python scripts while building the
initial model.

#### Flags and Toggles
If you want to toggle some behavior in data generation, logging, et cetera, you need to (1) add a flag to the HJSON
script and (2) encapsulate the toggled behavior in an `if` guard. For example, say you want to toggle logging `.npz`
files. Add something like the following to your HJSON script:

```
log:
{
    log_npz: true  # new flag, with the behavior enabled
}
```

Then, in your logger, under `.post()`:

```python
if self.cfg['log'].log_npz:
    # log npz files here
```


### Style Guidelines
When in doubt, refer first to the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html), then
to [PEP 8](https://www.python.org/dev/peps/pep-0008/) and [PEP 257](https://www.python.org/dev/peps/pep-0257).



## Credits
- MacLean Lab (maintainers)
- Maass Group (collaborators)

## License
This software and associated documentation have been made open source under
the [MIT License](https://opensource.org/licenses/MIT).
