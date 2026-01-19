# Digital Voting

This repository contains code and resources related to digital voting systems. It is an attempt to create a simple platform for conducting digital votes.

## Setup on Linux

To set up the project, follow these steps:
1. Clone the repository:
   ```bash
   git clone https://github.com/gratach/digital-voting.git
    ```
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```
3. Activate the virtual environment:
    ```bash
    source venv/bin/activate
    ```
4. Navigate to the project directory:
   ```bash
   cd digital-voting
   ```
5. Install the project editably:
   ```bash
   pip install -e .[dev]
   ```

## Running Tests

To run the tests, use the following command in the virtual environment:

```bash
pytest
```