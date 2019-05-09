# GitHub Metrics

Dependencies:
  - python3
  - all of the packages listed on requirements.txt
  
To install the python packages:

  ```
  pip install -r requirements.txt
  ```
  
To run:
  - Set the variables in run.sh
    - GitHub Token: you will need to generate your own GitHub access token
    - Organization name: you will need to insert the organization name to search for its repositories
    - StartsWithText: a filter that filters the analysed projects by name (For example, when startswithtext is set to 2019.1, the following repositories would be analysed: 2019.1-AnyName, 2019.1-OtherName. And the following would be ignored: 2018.2-Name, 2017.1-AnotherRepo)
    
  - Run the executable
  ```
  ./run.sh
  ```
  
The results will be inserted into a folder with the organization name in the executable's path.
