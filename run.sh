#!/bin/bash
# To set a value to a variable, simply type the value without quotation marks
token= # Insert your GitHub token here
startswithtext=2019.1 # If you want only the repos which the name starts with '2019.1', for example, set this variable to 2019.1
organization=fga-eps-mds # Insert the name of your organization here

if [ -z "$organization" ]
then
    echo "You have not specified any GitHub organization to fetch data! Edit run.sh and add your GitHub organization name."
else
    if [ -z "$token" ]
    then
        echo "GitHub access token not found! Edit run.sh and add your GitHub access token."
    else
        GITHUB_ORGANIZATION=$organization STARTS_WITH_TEXT=$startswithtext GITHUB_TOKEN=$token python3 core.py
    fi
fi