#### Dump Trivy Operator reports.
- Official CRDs reference: [CRDs](https://aquasecurity.github.io/trivy-operator/latest/docs/crds/)

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

#### How to list cluster objects:
```bash
./env/bin/python3 main.py resource_types
```
```bash
./env/bin/python3 main.py list_resources --type="clusterinfraassessmentreports"
```

#### How to list namespaced objects:
```bash
./env/bin/python3 main.py resource_types --namespaced
```
```bash
./env/bin/python3 main.py list_resources --type="vulnerabilityreports"
```

#### How to dump cluster objects:
```bash
./env/bin/python3 main.py resource_types
```
```bash
./env/bin/python3 main.py dump_resources --type="clusterinfraassessmentreports"
```

#### How to dump namespaced objects:
```bash
./env/bin/python3 main.py resource_types --namespaced
```
```bash
./env/bin/python3 main.py dump_resources --type="vulnerabilityreports"
```
