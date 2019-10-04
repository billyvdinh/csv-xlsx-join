# How to ...

## Clone repository from github

```git clone https://github.com/mbpup/multifile_joiner.git```

## Running script

```cd  multifile_joiner/```

### Install dependencies

```pip install -r requirements.txt```

### Run Script

```python main.py --set dir=<data directory path> output=<output file path>```

For example, if you have all the csv/xlsx files in the ```data/``` directory, you can run script as follow:

```python main.py --set dir=data/ output=data/data.csv```