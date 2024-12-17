## Pull Request Checklist

### Summary
- [ ] Pull request has a descriptive name
- [ ] Briefly describe the purpose of this pull request.
- [ ] Link any relevant issue numbers (e.g., `Fixes #123`).
- [ ] Add the milestone of the sprint

### Code Changes
- [ ] The code changes are clearly described
- [ ] Code is PEP8 compliant 
    (Pylint can be used to show real time issues, Black can be used to enforce)
- [ ] Are only the relevant files included in the commits (e.g. no pycache or log file)

### Documentation
- [ ] Are there sufficient in line comments?
- [ ] Is there a docstring for each function or class in Numpy format
- [ ] Is there top level documentation in the file and is it up to date
- [ ] Has the README been updated if relevant

### Dependencies
- [ ] Are there any new dependencies?
- [ ] Have the dependencies been added to the requirements file or environment file with version?

### Testing
- [ ] This PR has been tested locally.
- [ ] Automated tests have been added or updated as needed.
- [ ] Tests pass without errors.
- [ ] Logging statements added (if it's a core script)

### Review and Approval
- [ ] Self-review completed.
- [ ] Ready for team review.

### Comments
e.g. How to run tests if any data needed...