# JIRA Invoice
Tempo time data and JIRA work data for the selected time frame are summarized to either the Epic or the Story/Bug level (depending on data).
Hours may be entered on Sub-Tasks, Stories or Epics.
The exported csv can easily be used to create a final format invoice.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites
You need Python 3.4 or later to run JIRAInvoice and the latest version of virtualenv to create the runtime environment.  

```
$ sudo apt-get install python3 python3-pip

```

### Installing

The steps below will clone a copy of the code to your local machine, create a virtual environment and setup any dependencies.

```
$ git clone https://github.com/ronjohn4/JIRAinvoice  
$ virtualenv JIRAinvoice --python=python3
$ cd JIRAinvoice
$ source ./bin/activate
(JIRAinvoice)$ python setup.py install
```

### Running

The command below will start up JIRAinvoice in your default webserver on port 5002 (this can be changed in the code).

```
$ python JIRAinvoice.py
```

The address where the app is running will be displayed on the command line.  Simply navigate to this address in your browser.
Use a CTRL+C to stop the app.