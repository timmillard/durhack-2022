<h1 style="display:inline">Pulsifi<small> - The most intense social media platform in existence</small></h1>

Created for Durhack 2022

By Tim Millard, Padgriffin, Charlie Simpson and Charlie Wilson

<sub><sup>Additional help from [@CarrotManMatt](https://github.com/CarrotManMatt "CarrotManMatt's Github Page")</sup></sub>

<h2>How to Start Developing Pulsifi</h2>
<ol>
  <li>Create a new branch to begin developing from by going to <nobr>the <a href="https://github.com/timmillard/durhack-2022/branches" title="The branch management page of the Pulsifi GitHub repository">branch management page</a></nobr> of this repository and clicking the <nobr><code>New branch</code></nobr> button</li>
  <li>Give your branch a suitable name and choose the most recently updated branch as the source <nobr>(most often this will be the <a href="https://github.com/timmillard/durhack-2022/tree/matt-changes" title="Hello!"><code>matt-changes</code> branch</a>)</nobr></li>
</ol>
<ul>
  <li>
    <h3>VS Code:</h3>
    <ol start="3" type="1">
      <li>Now select your newly created branch from the list & copy the https download link using the <nobr>green <nobr><code>˂˃ Code ▼</code></nobr> button</nobr></li>
      <li>Open/run VS Code and make sure the <nobr><a href="https://marketplace.visualstudio.com/items?itemName=ms-python.python" title="VS Code Python extension">Python extension</a></nobr> is installed, as well as the <nobr><a href="https://www.python.org/downloads/" title="Latest version of Python">latest major version of Python</a></nobr></li>
      <li>Open the Source Control view panel by clicking the tree icon on the far left-hand side</li>
      <li>Select <nobr><code>Clone Repository</code>,</nobr> and paste the copied repository URL into the <nobr>Git: Clone</nobr> prompt</li>
      <li>Select <nobr><code>Clone from GitHub</code></nobr> <nobr>(this is usually the second option in the list dropdown),</nobr> and authenticate your GitHub account with VS Code if necessary</li>
      <li>If the prompt still persists <nobr>(and is asking for the <code>Repository name</code>),</nobr> <nobr>enter "timmillard/durhack-2022"</nobr> to search for the repository, and select the correct one from the dropdown list</li>
      <li>Choose the local directory that you would like to use to store a local copy of the <nobr>checked-out</nobr> parts of the repository</li>
      <li>Ensure your newly created branch is checked out for you to work on by making sure the name of your branch is shown below the settings cog in the <nobr>bottom-left-hand corner</nobr></li>
      <li>Use the <nobr><code>Ctrl+Shift+`</code> keyboard shortcut</nobr> to create and open a new terminal panel at the current directory</li>
      <li>Create and activate a new Python virtual environment using the <nobr><code>py -3 -m venv .venv</code></nobr> and <nobr><code>.venv\scripts\activate</code></nobr> commands (make sure these commands are run within the directory containing your local copy of the repository)</li>
      <li>Update the pip package with this command: <nobr><code>python -m pip install --upgrade pip</code></nobr></li>
      <li>Install all the required packages for Pulsifi using this command: <nobr><code>pip install -r requirements.txt</code></nobr></li>
      <li>You can now make the edits you desire to the code within your branch</li>
      <li>If you make any changes to the <nobr><code>models.py</code></nobr> file you need to migrate these changes to the database by running these commands: <nobr><code>py manage.py makemigrations</code></nobr> and <nobr><code>py manage.py migrate</code></nobr> (it is also a good idea to run both of these commands, just in case, before committing any changes)</li>
      <li>
        Any changes you do make will show up under the changes list, within the <nobr>Source Control view panel</nobr> on the left-hand side. These changes can be committed to your branch then pushed to the remote repository by:
        <ol start="1" type="1">
          <li>Adding them to the staging area, by clicking the <nobr><code>+</code>(plus) button</nobr> next to any of the desired changed files in the changes list</li>
          <li>Typing a useful commit message in the <nobr><code>Message</code> text-input box</nobr> <nobr>(see <nobr><a href="https://gist.github.com/robertpainsi/b632364184e70900af4ab688decf6f53" title="Robert Painsi's Commit Message Guidelines">Robert Painsi's Commit Message Guidelines</a></nobr>,</nobr> for how to write good commit messages)</li>
          <li>Clicking the checkmark at the top of the Source Control view panel, to commit your changes to your branch</li>
          <li>Clicking the <nobr>refresh/pull/push/update button,</nobr> on the status bar, in the <nobr>bottom-left-hand</nobr> corner next to your currently <nobr>checked-out</nobr> branch name, to push your commits to the remote repository</li>
        </ol>
      </li>
      <li>To run the development server, use the <nobr><code>py manage.py runserver localhost:8080</code></nobr> command, then navigate to <nobr><a href="http://localhost:8080"><code>http://localhost:8080</code></a></nobr> to view the site</li>
      <li>To run the test suite, use the <nobr><code>py manage.py test</code></nobr> command</li>
    </ol>
  </li>
  <li>
    <h3>Pycharm (Preferred):</h3>
    <ol start="3" type="1">
      <li>...</li>
    </ol>
  </li>
  <li>
    <h3>Using the git commandline & an alternative IDE:</h3>
    <ol start="3" type="1">
      <li>...</li>
    </ol>
  </li>
</ul>

<h2>Programming Conventions</h2>
<ul>
  <li>Always use double quotes, unless inside an HTML template variable string within an HTML tag attribute <nobr>(E.g. <code>&lt;a href="{% url 'default' %}"&gt;&lt;/a&gt;</code>)</nobr></li>
  <li>Never put commas after the last item in a list/dictionary <nobr>(E.g. <nobr><code>["a", "b", "c"]</code></nobr>, not <nobr><code><del>["a", "b", "c",]</del></code></nobr>)</nobr></li>
  <li>Model names are capitalised <nobr>(E.g <code>Post</code>)</nobr></li>
  <li>View names are capitalised, end in <nobr><code>View</code></nobr> and have words seperated by underscores <nobr>(E.g. <code>Feed_View</code>)</nobr></li>
  <li>Constants, settings values and field choices are uppercase and have words seperated by underscores <nobr>(E.g. <code>STATIC_URL</code>)</nobr></li>
  <li>Model field names are lowercase, must not contain the model name and have words seperated by underscores <nobr>(E.g. <code>date_time_created</code>, not <code><del>postDateTimeCreated</del></code>)</nobr></li>
  <li>HTML template names are lowercase and have words seperated by underscores <nobr>(E.g. <code>feed.html</code>)</nobr></li>
  <li>Please use comments and docstrings to help others understand code functionality</li>
  <li>Be very cautious when using <nobr><code>QuerySet.update()</code>,</nobr> as this will *NOT* execute the <nobr><code>save()</code></nobr> method of each object instance (which is essential to ensure data integrity & validity). There are unlikely to be cases where the performance decrease of using the custom <nobr><code>Custom_Model.update()</code></nobr> method, on each instance individually, is so significant that <nobr><code>QuerySet.update()</code></nobr> has to be used. If in doubt, iterate through each instance with a <nobr><code>for</code> loop,</nobr> and call <nobr><code>Custom_Model.update()</code></nobr> individually.</li>
  <li>Never use any bulk edit functions <nobr>(E.g. <nobr><code><del>QuerySet.delete()</del></code>,</nobr> <nobr><code><del>QuerySet.bulk_create()</del></code>,</nobr> <nobr><code><del>QuerySet.bulk_update()</del></code>,</nobr> etc.)</nobr>, as these will not execute the respective, overridden <code>Model.save()</code> or <code>Model.delete()</code> methods (which is essential to ensure data integrity & validity).</li>
</ul>