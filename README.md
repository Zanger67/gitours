# CS4675-6675_Group_14

## Launching the BackEnd
In order for the application function correctly, both the front-end React.js app and the
back-end Python Flask app need to be running at the same time. To launch the Flask back-end,
navigate to the `backend` directory and input the command `python backend.py` into your
terminal. `backend.py` needs to continue running in a terminal, so you will need to use
a 2nd simultaneous terminal instance to launch and support the front-end.

## Using the App
After downloading the neccessary packages to run next.js, you can start up a test-build of
the app by navigating to the `githubsummarizer` directory in your terminal and then using the
command `npm run dev`.

## Important App Files
In the `githubsummarizer` directory, the JavaScript and CSS files that make up the app's pages
can be found in the `src/app` folder.

As of now, the only files in the source directory that are worth paying attention to are
`page.js`, `exampleText.js`, and `globals.css`.

- `page.js` contains the JavaScript code that makes up the app's one and only (as of now) page.
- `exampleText.js` contains constants and methods that are intended to be used for testing, and may be removed later.
- `globals.css` contains the CSS code for the app's one and only (as of now) page.

### Versions
- Version 0.1: Created skeleton for app front-end. The app has a basic UI consisting of a textfield for the user to input a link to a GitHub repository, and a textarea where the contents of a JSON file will appear. There is also a button below the textarea to download the textarea's current contents as a JSON file to the user's device. The textfield currently only checks if the input string starts with `https://` when the user clicks on the submit button. If so, then a success message will appear, and the textarea will be populated with example data. This example data will always be the same regardless of the link that was input by the user.
- Version 0.2: Back-end functionality has been added, and can be linked to the front-end app.