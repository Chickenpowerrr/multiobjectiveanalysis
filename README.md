# Multi-objective Benchmark
This Python programming evaluates multi-objective numerical queries 
both by querying the result directly and by approximating it through
multi-objective achievability queries. This helps us to get insight into
how multi-objective model checking tools perform and attempt to find 
mistakes in their implementation.

## Structure
- [models](models) contains all models and multi-objective numerical properties that are analysed
- [results](results) contains reference results, will also contain your own results if you run the tool
- [scripts](scripts) contains the code to generate new results

## Analysing our results
Here we list all directories which we published.
### [1714292638047](results/1714292638047)

#### Settings
Can be found in [settings.yml](results/1714292638047/settings.yml).

####  Used versions
- Ubuntu 22.04.4 LTS
- OpenJDK 21.0.2 (https://jdk.java.net/21/)
- Python 3.10.12 (https://www.python.org/downloads/release/python-31012/)
- pip 22.0.2 (sudo apt install python3-pip)
- Storm 1.8.1 (https://github.com/moves-rwth/storm/releases/tag/1.8.1)
- PRISM 4.8.1 (https://github.com/prismmodelchecker/prism/releases/tag/v4.8.1)
- ePMC (revision b1ba8ab) (https://github.com/iscas-tis/ePMC/tree/b1ba8abf9f52c05f23421efb1abd1be7618f426d)
- Spot 2.11+ (https://spot.lre.epita.fr/install.html)

#### Used environment
A Lenovo Thinkpad, with an Intel i7-13700H with 14 cores and 32GB of RAM, on Windows 11, build 22631.3447 which ran the experiments using WSL.

## Replication

### Prerequisites
- Ubuntu
- Git (sudo apt install git)
- Java 13+ (sudo apt install openjdk-21-jdk)
- Python 3.6+ (sudo apt-get install python3.11)
- Pip (sudo apt install python3-pip)
- Storm (https://www.stormchecker.org/getting-started.html)
- PRISM (https://www.prismmodelchecker.org/download.php)
- ePMC (https://tis.ios.ac.cn/epmc/doku.php?id=main)
- Spot (https://spot.lre.epita.fr/install.html)

### Running the script
First of all, the project needs to be cloned:
```git clone https://github.com/Chickenpowerrr/multiobjectiveanalysis.git```

After that, we can run the script by going into the scripts directory:
```cd multiobjectiveanalysis/scripts```

We then need to install the Python packages:
```pip3 install -r requirements.txt```

After that, we can run the script for the first time:
```python3 main.py```

Most likely the program now crashes. The script has generated a `settings.yml`
file. In here, you need to set the paths to the model checkers, java and spot.
After that the program should work by simply running:
```python3 main.py```
