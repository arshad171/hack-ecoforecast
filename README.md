# SE-Europe-Data_Challenge_Template
Template repository to work with for the NUWE - Schneider Electric European Data Science Challenge in November 2023.

# Tokens:
- b5b8c21b-a637-4e17-a8fe-0d39a16aa849
- fb81432a-3853-4c30-a105-117c86a433ca
- 2334f370-0c85-405e-bb90-c022445bd273
- 1d9cd4bd-f8aa-476c-8cc1-3442dc91506d

# Running the Pipeline (Examples)

The individual steps can be run by commenting out the respective sections in the [run_pipeline.sh](./scripts/run_pipeline.sh) file. **All the parameters passed here are folder names, rather than specific a filename**. This will make it easier to dump all the necessary data at each state.

Run the following:
`sh scripts/run_pipeline.sh 2022-01-01 2023-01-01 data-raw data-processed models data-processed predictions`

# Repository

Practices:

- Requirements

- Best practices are followed by writing clean and efficient code (utilize numpy/TF ops whereever possible).

- The code is typed to provide documentation and type hints.

- All the configs and hyperparams go under [config](./src/config.py).

- All the constatns are defiend in [constants](./src/constants.py).

# Documentation

- [Data Analysis](./data-analysis.md)

- [Machine Learning](./machine-learning.md)