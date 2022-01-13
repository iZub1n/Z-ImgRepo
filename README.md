
# Z-ImgRepo

Live Demo: https://z-imgrepo.herokuapp.com/

Shopify Developer Intern Challenge: https://docs.google.com/document/d/1eg3sJTOwtyFhDopKedRD6142CFkDfWp1QvRKXNTPIOc/edit

An Image Repository. Implemented using Python (Flask), PSQL, JavaScript, HTML and Amazon S3

This is an Image Repository which allows users to create accounts and upload pictures. It also users to view other's upload. Lastly, users can search images based on tags and uploaders. Searching similar images is also supposrted

## How To Use 
There are 2 options to use this application. Visiting the website (https://z-imgrepo.herokuapp.com) or installing it on your machine. The First option being the best

If choosing the latter:
### Instructions - How To Install
1. Clone the git repository on to your machine
2. Open the directory
3. Use the terminal to access this directory
4. Run: `python3 -m venv venv`
5. Run: `source venv/bin/activate`
6. Run: `pip install -r requirements.txt` Wait for it to install, this may take some time
7. Run: `export FLASK_APP=application.py`
8. Run: `export DATABASE_URL=postgres://otnuugehoevpcc:4e30c302650373c04e027740d350352f85bf0195ab8447587def58d67ba693a0@ec2-3-216-89-250.compute-1.amazonaws.com:5432/d3g7n801clnsub`
NOTE: This method doesn't support uploading files as files are uploaded to Amazon AWS S3. This method requires the perosn running the app locally to have access to my credentials which I deem unsafe.
9. Run: `flask run` . The website should now be live locally at http://127.0.0.1:5000/

### User Login
1. The user is directed to a login page where they can use a preexisting account or create a new one
NOTE: All pages have a navbar after loggin in

### Navigating The Repository
1. After loggin in the user is directed to the homepage which displays an image along with its infomation.
2. The Feed Page shows images from users the account is following
3. The Discover page shows images from all users in reverse chronological order
4. Clicking on your username displays the user page
5. The user page contains information about the user and displays one of their pictures. You can also see who the user follows and they are followed by. These accounts can also be visited
6. Uploading and Searching are discussed below

### How To Add Images
1. Click on you username
2. Click Add +
3. Here you can add a caption, add various tags seperated by commas (ex: tag1, tag2, tag3) and finally choose picture(s) to upload
NOTE: Multiple pictures being uploaded together are treated as part of the same upload and hence share the caption and tags
4. Click the upload button. One you get a green banner saying success, your uploads are now visible on the repository

### How to Search
Images can either be searched using the search bar or through other similar images.

#### Using the Search bar
1. Enter a tag or username to search. The tag or username can just be a part of the query and not the whole word (ex: at will search for cat and atom) if the exact search option is checked off.
2. If the Exact search option is checked the user must input exact tags and usernames for results to show up. This is not case sensetive

#### Using Other Images to Search
1. Each Image has tags
2. Clicking on a specific tag will show other images on the repository sharing the same or similar tags
3. The user can also use the name of the uploader in the searchbar to find more images by that specific person

#### Screenshots

![Screen Shot 2022-01-09 at 6 17 18 PM](https://user-images.githubusercontent.com/60079441/148705283-a22ea1b1-ed13-44e5-b887-7f12de9886fb.png)

![Screen Shot 2022-01-09 at 6 17 28 PM](https://user-images.githubusercontent.com/60079441/148705299-bbe73d2a-2cf3-427a-a8c3-8bf489058d9c.png)

![Screen Shot 2022-01-09 at 6 17 53 PM](https://user-images.githubusercontent.com/60079441/148705305-9b62dbee-4f04-490a-911a-630c705347cc.png)

![Screen Shot 2022-01-09 at 6 18 17 PM](https://user-images.githubusercontent.com/60079441/148705314-15b29780-9f99-479b-b4ed-1b277f0ebfba.png)

![Screen Shot 2022-01-09 at 6 18 27 PM](https://user-images.githubusercontent.com/60079441/148705317-1a897740-2e8d-4f93-97d7-e9b7f2433eb1.png)

