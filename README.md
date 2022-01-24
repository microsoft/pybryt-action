# PyBryt Action

An action for running [PyBryt](https://microsoft.github.io/pybryt) as an automated assessment tool on GitHub repositories.

### GitHub Actions 
If your not familar with GitHub Actions or Workflows we advise you to complete this short awarness module [GitHub Actions, Microsoft Learn Module](https://docs.microsoft.com/learn/modules/introduction-to-github-actions) By the end of this module, you'll be able to:

- Explain GitHub Actions and workflows
- Create and work with GitHub Actions and Workflows
- Describe Events, Jobs and Runners
- Examine output and release management for actions

## Usage of PyBryt GitHub Action

The PyBryt action accepts the following inputs:

| Name | Required | Description |
|-----|-----|-----|
| `submission-path` | yes | The path to the submission file to run |
| `references` | yes | A newline-delimited list of paths or URLs to reference implementations |
| `additional-files` | no | A newline-delimited list of file paths to also trace when executing the submission |

For example, to run PyBryt on the [Fibonacci demo in the main repo](https://github.com/microsoft/pybryt/tree/main/demo/fibonacci), you could use

```yaml
name: Run PyBryt

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Run PyBryt
        uses: microsoft/pybryt-action@main # TODO: update the version
        with:
          submission-path: demo/fibonacci/submissions/subm01.ipynb
          references: |
            https://raw.githubusercontent.com/microsoft/pybryt/main/demo/fibonacci/fibonacci_dyn.pkl
            https://raw.githubusercontent.com/microsoft/pybryt/main/demo/fibonacci/fibonacci_map.pkl
            https://raw.githubusercontent.com/microsoft/pybryt/main/demo/fibonacci/fibonacci_no_recurse.pkl
```

If you were using a notebook as a testing harness, you may want something like:

```yaml
- name: Run PyBryt
  uses: microsoft/pybryt-action@main # TODO: update the version
  with:
    submission-path: harness.ipynb
    additional-files: |
      student_code.py
    references: |
      references/fibonacci_dyn.pkl
      references/fibonacci_map.pkl
      references/fibonacci_no_recurse.pkl
```

## Outputs

PyBryt will always print a report for each reference to the console, but it also outputs relevant artifacts to a few files that can be used for further processing.

| Name | Description |
|-----|-----|
| `report-path` | Path to a `.txt` file containing the report generated by PyBryt (the same one printed to the console) |
| `results-path` | Path to a `.pkl` file containing the pickled list of results objects generated by PyBryt |
| `student-implementation-path` | Path to a `.pkl` file containing the pickled student implementation object generated by PyBryt from the submission |

For example, you may want to commit these as files in the student's repo:

```yaml
- name: Run PyBryt
  id: pybryt
  uses: microsoft/pybryt-action@main # TODO: update the version
  with:
    # etc.
- name: Save, commit, and push results
  run: |
    mkdir -p results
    cp ${{ steps.pybryt.outputs.report-path }} results/report.txt
    cp ${{ steps.pybryt.outputs.results-path }} results/results.pkl
    cp ${{ steps.pybryt.outputs.student-implementation-path }} results/student-implementation.pkl
    git add results
    git commit -m "PyBryt results for ${{ github.sha }}"
    git push
```

With these files, you could use a script like this to unpickle these objects in Python:

```python
import dill
import os
import pybryt

RESULTS_DIR = "results"

results: list[pybryt.ReferenceResult]
student_impl: pybryt.StudentImplementation

with open(os.path.join(RESULTS_DIR, "results.pkl"), "rb") as f:
  results = dill.load(f)

student_impl = pybryt.StudentImplementation.load(os.path.join(RESULTS_DIR, "student-implementation.pkl"))
```
## Enhancing your Github Actions 

If you are interesting, in learning how GitHub Actions enables you to automate your software development cycle and deploy applications we recommend the following short course [Automate your workflow with GitHub Actions](https://docs.microsoft.com/learn/paths/automate-workflow-github-actions/)

In this learning path, you'll:

- Plan automation of your software development life cycle with GitHub Actions workflows.
- Use GitHub Actions to automatically build your application.
- Deploy to Microsoft Azure with GitHub Actions.
- Use GitHub Script to interact with the GitHub API.
- Publish automatically and securely your code libraries or Docker images with GitHub Packages.

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
