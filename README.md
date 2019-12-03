# Bookmark-Manager
NLP based approach to automatically categorize your bookmarks!

## In-Depth
To understand this project in-depth, refer to my technical paper: [Bookmark Classification using Multinomial Naive Bayes Model](https://pncnmnp.github.io/blogs/bookmark-classification.pdf)

## How does this work ?
* Enter your bookmarks in **`./links.json`** file
* To run the code, run `categorize.py`
* `scrape_filter_link.py` contains the classes used to scrape information from each URL

## What bookmarks is it categorizing ?
It can categorize a variety of bookmarks. Currently it supports all the categories mentioned in the `./corpus/` directory.

## Will I have to enter my bookmark links manually ?
To a certain extent! For example: **Firefox** allows users to backup the bookmarks in a JSON format. You can extract the `uri` from that JSON file and feed it into `./links.json`.<br/>
To backup your bookmarks in **Firefox**, press Ctrl+Shift+O, go to `Import and Backup` and then to `Backup`.<br/>
**Chrome** users can check this post on [superuser](https://superuser.com/questions/325394/how-to-export-my-bookmarks-via-cli-in-google-chrome/1349857).

## Will the code create a directory structure with my bookmarks ?
**No, the mapping of a URL with it's appropriate category is stored in a JSON file: `result.json`, in a *dict* format**.<br/>
The keys are your bookmarks with values being their categories.

## Can I see a demo ?
Sure, here's one (The highlighted part is the one stored in `result.json`):
![Bookmark-Manager output](https://i.imgur.com/ZcIAyvy.png)

## Can I improve the corpus, by adding more categories in `./corpus/` directory ?
**Yes, you can! The code is fairly scalable.**<br/>
To add your own corpuses: 
* Create a directory with a *unique* category name in `./corpus/`
* Inside the `./corpus/your-category-dir` add your corpus text in a **JSON** file with the format: `{"text": "_your_corpus_text_here_"}`

(**NOTE:** You can add multiple JSON files in a category directory)<br/>
When you run the code, you will find that the `categorize.py` will take the new/modified corpuses into consideration.

## License
The code is under MIT License
