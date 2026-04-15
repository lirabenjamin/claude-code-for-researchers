---
name: data-analysis
description: This is default workflow for data analysis. It includes steps for data cleaning, exploration, and visualization.
---

This is the process I want to follow for data analysis:

1. Download the data. Usually this means getting it from Qualtrics using the qualtRics R package, but it could also be from a CSV file or an API.

One example of how to download data from Qualtrics using the qualtRics R package is as follows:

```R
id = "SV_1Bn8JHpeFDRuu5E"

library(qualtRics)

fetch_survey(
  surveyID = id,
  verbose = TRUE,
  force_request = TRUE,
  convert = FALSE
) -> data

attr(data, "column_map")
```
Note that you can use attr(data, "column_map") to get the column names and their corresponding question IDs, which can be helpful for data cleaning and analysis.

2. Create a data cleaning file (00 clean.r). This will include steps for handling missing data, recoding variables, and creating new variables as needed.

Make sure to only keep the variables that are necessary for the analysis and nothing else.
Make sure all variables have good names
Make sure to drop all cases that are not needed (e.g., previews, etc.) If applicable, only keep participants who have a PROLIFIC_PID, and drop all cases that do not have a PROLIFIC_PID. This will ensure that you are only analyzing data from participants who completed the survey on Prolific.
If there is a row where PROLIFIC_PID is "{{%PROLIFIC_PID%}}" then drop that row.


3. Create an exploratory data analysis (EDA) file (01 eda.r). This will include steps for summarizing the data, creating visualizations, and identifying any patterns or trends in the data. 

This file outputs a full correaltion matrix for all variables (and sub matrices if it helps interpretation). Histograms for all variables. Checks for outliers, etc. Output everything as a series of plots to a subfolder called eda.

4. Create a final analysis file. This will include steps for conducting any statistical analyses, creating final visualizations, and writing up the results. This will be a qmd file.

This should have all the final analyses and visualizations, and should be written up in a clear and concise manner. Make sure to include all relevant information, such as the sample size, the statistical tests used, and the results of those tests.
DO NOT use cat to show results, instead use `r results` to show results in the quarto document. This will make it easier to read and understand the results.
Make the code hideable
Make sure the code is runnable interactively or from the quarto document. This will allow you to easily test and debug your code, and also make it easier for others to understand and reproduce your analysis. For example:

```R

# switch for data load.
is_running_in_quarto <- function() {
  # Check if a Quarto-specific environment variable is set
  return(Sys.getenv("QUARTO_DOCUMENT_PATH") != "")}

# Example usage:
if (is_running_in_quarto()) {
  dat <- read_parquet("../data/processed/analysis_data.parquet")
  fig_path <- "../output/figures/"
  tab_path <- "../output/tables/"
} else {
 dat <- read_parquet("./data/processed/analysis_data.parquet")
 fig_path <- "./output/figures/"
 tab_path <- "./output/tables/"
}
```

Before submitting your work, always read the rendered report to make sure your reporting makes sense: for example if you wrote A and B were positively correlated (r = 0.023, p = 0.523), then you need to fix your write up.

Some rules:
- Always use the same file structure for each project. This will make it easier to find files and keep things organized.
- Use clear and descriptive names for files and variables. This will make it easier to understand what each file and variable is for.
- Document your code thoroughly. This will make it easier for others (or yourself in the future) to understand what you did and why you did it.
- Use version control (e.g., Git) to track changes to your code and collaborate with others. This will help you keep track of changes and avoid losing work.
- Always test your code to ensure it works as expected. This will help you catch any errors or bugs before they become a problem. Make sure you run the quarto document to make sure everything is working.
- Absolutely NO MAGIC NUMBERS. Don't hard code any statistics, instead calculate them from the data. This will ensure that your analysis is reproducible and that you can easily update your results if you need to make changes to your data or analysis.
