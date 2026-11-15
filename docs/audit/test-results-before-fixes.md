# Tests on the original ZIP source

The tests were run from the untouched staging copy extracted from the original ZIP, using the project Python 3.11 environment after its dependencies were installed:

```powershell
python -m pytest -q apps\api\tests services\rotation-engine\tests
```

Result: **52 passed**, one warning from the installed AnyIO pytest plugin importing pytest's deprecated `CallSpec2` alias. No failures or collection errors.

This is the original ZIP's test baseline, not a reconstructed pre-fix run of the workspace architecture scaffold. The archive did not contain a separate build or frontend test runner. Browser developer-console inspection was stopped by the computer-use policy helper because it could not establish the current browser URL; local HTTP checks were used for the running page and API.
