# P8 Windows installs

Plan: `docs/implementations/2026-10-14-solo-prototypes.md`. Run 2026-10-14T06:41:06Z on Windows-11-10.0.26300-SP0; base Python 3.13.14; fresh virtual environment; pip 26.2.1 from C:\Users\senso\chorus-runs\proto-p8-venv\Lib\site-packages\pip (python 3.13). Packages installed one at a time at their latest versions (owner's choice).

| Requirement | Install | Built from source | Version | Import | Note |
|---|---|---|---|---|---|
| huggingface_hub[hf_xet] | ok | no | 2.2.0 | ok |  |
| hf_xet | ok | no | 1.7.0 | ok |  |
| safetensors | ok | no | 0.8.0 | ok |  |
| cryptography | ok | no | 50.0.2 | ok |  |
| iroh | ok | no | 1.1.0 | ok |  |
| libp2p | ok | yes | 0.8.0 | ok |  |

Total time: 232.5 s. `pip freeze` of the environment is in the JSON file.
