# Project metrics

## About

Visualization of project metrics for git projects.

- Number of commits per author in specific period of time
- Number of commits per keyword in specific period of time (deployment frequency)

## Commits per author script

Run script with command:

`python3 commits_per_author.py`

Input parameters:
- Author name (git name)
- Git repositories
- Git branches
- Start week
- End week

Example:
- Enter author name: jciberlin
- Enter paths to git repos (comma or space separated): ../IMUtility ../IMBootloader
- Enter branches (comma or space-separated): main master
- Enter week-from (YY.WW, blank for none): 22.1
- Enter week-to (YY.WW, blank for none): 23.1

Result:
![alt text](https://github.com/jciberlin/ProjectMetrics/blob/main/example_result/commits_per_author/commits_jciberlin_IMUtility_IMBootloader_main_master_22.1_23.1_weeks.png?raw=true)

![alt text](https://github.com/jciberlin/ProjectMetrics/blob/main/example_result/commits_per_author/commits_jciberlin_IMUtility_IMBootloader_main_master_22.1_23.1_months.png?raw=true)

## Commits per keyword script

Run script with command:

`python3 commits_per_keyword.py`

Input parameters:
- Keywords
- Git repositories
- Git branches
- Start week
- End week

Example:
- Enter keywords inside quotes (e.g. "misra" "bug" "fix"): "misra" "priority queue"
- Enter paths to git repos (comma or space separated): ../IMUtility
- Enter branches (comma or space-separated): main
- Enter week-from (YY.WW, blank for none): 23.1
- Enter week-to (YY.WW, blank for none): 24.11

Result:
![alt text](https://github.com/jciberlin/ProjectMetrics/blob/main/example_result/commits_per_keyword/commits_keywords_misra_priority_queue_23.1_24.11_weeks.png?raw=true)

![alt text](https://github.com/jciberlin/ProjectMetrics/blob/main/example_result/commits_per_keyword/commits_keywords_misra_priority_queue_23.1_24.11_months.png?raw=true)

## Info
Script is tested on Ubuntu 18.04.6 LTS using Python 3.6.9 version. 
