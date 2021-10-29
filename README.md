# Project Setup

## Table of Contents

- [Project Setup](#project-setup)
  - [Table of Contents](#table-of-contents)
    - [Run project locally](#run-project-locally)
      - [Install Requirements](#install-requirements)
      - [Run script](#run-script)

### Run project locally


#### Install Requirements

- Ensure virtual environment is activated and run command

        pip install -r requirements.txt

- To create virtual environment and activate

        python venv -m venv
        source venv/bin/activate

#### Run script

- Run command

        python scrape.py -r 50 -z 1000231

        where:
        -r: radius to be used
        -z: zipcode to be used
