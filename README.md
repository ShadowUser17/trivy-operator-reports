#### Template Python project...

#### Configure environment:
```bash
python3 -m venv --upgrade-deps env && \
./env/bin/pip3 install -r requirements_dev.txt
```

#### Scan project dependencies:
```bash
./env/bin/pip-audit -f json | python3 -m json.tool
```

#### Validate project files:
```bash
./env/bin/flake8 --ignore="E501" *.py
```
