# cae-test-revocation

Python script for testing **Continuous Access Evaluation** (CAE) refresh/access token revocation.

## How to run

```powershell
# Create and activate a virtual environment
python -m venv env
. .\env\Scripts\Activate.ps1

# Clone repos
git clone https://github.com/jiasli/cae-test-revocation
git clone https://github.com/Azure/azure-sdk-for-python

# Install Python SDK source code
cd azure-sdk-for-python
git checkout feature/cae
pip install --editable sdk\resources\azure-mgmt-resource
pip install --editable sdk\identity\azure-identity
pip install --editable sdk\core\azure-core
cd ..

# Run the test script
cd cae-test-revocation
python test_cae_revocation.py
```

## Reference

- The original script: https://gist.github.com/chlowell/297b3200f6300260eb67023a242ac0d3
- Python SDK development branch for CAE support: https://github.com/Azure/azure-sdk-for-python/tree/feature/cae
- .NET test script: https://github.com/erich-wang/MsalTestApp
