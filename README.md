# Movies ETL

> Extract the Wikipedia and Kaggle data from their respective files and insert into a SQL database.

## Summary

Amazing Prime loves the dataset and wants to keep it updated on a daily basis. Britta needs your help to create an automated pipeline that takes in new data, performs the appropriate transformations, and loads the data into existing tables. You’ll need to refactor the code from this module to create one function that takes in the three files—Wikipedia data, Kaggle metadata, and the MovieLens rating data—and performs the ETL process by adding the data to a PostgreSQL database.

### Resources

Python
PostgreSQL
CSV Files:

- ratings.csv
- movies_metadata.csv

JSON Files:

- wikipedia-movies.json

### Results / Analysis

Britta is excited to prepare for the hackathon where we gather data from both Wikipedia and Kaggle, combine them, and save them into a SQL database so that the hackathon participants have a nice, clean dataset to use. Raw data exists in multiple places and needs to be cleaned and structured before it can be analyzed. ETL breaks this problem into three steps, or phases: Extract, Transform, and Load. We had to play with two types of data that we are merging; one set comes in a json format that was scrapped from wikipedia and two csv files from Kaggle on movie reviews. You're going to follow an iterative process based on three key steps: plan, inspect, execute that we took within each Jupyter note file.

![Movies DB](resources/movies_query.png)

![Ratings DB](resources/ratings_query.png)

![Query in Pandas](resources/full_screen_grab.png)

## Todo Checklist

A helpful checklist to gauge how your README is coming on what I would like to finish:

- [ ] Lots of stuff.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
