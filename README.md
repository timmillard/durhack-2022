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
    <h3>Pycharm (Preferred):</h3>
    <ol start="3" type="1">
      <li>Open/run Pycharm and close all currently open projects in order to return to the <nobr><code>Welcome</code> window</nobr></li>
      <li>Click the <nobr><code>Get from VCS</code> button</nobr> in the top right corner of the window, then choose GitHub as the source on the left-hand side of the VCS pop-up window</li>
      <li>Log in to GitHub, then select the <nobr><code>timmillard/durhack-2022</code> repository</nobr> from the list</li>
      <li>Click the folder icon (<code>🗁</code>) on the far right-hand side of the <nobr><code>Directory</code> text-input box</nobr>, then create a directory called <b><nobr><code>Pulsifi</code></nobr></b> in a location of your choosing, to store a local copy of the <nobr>checked-out</nobr> parts of the repository (<em><b>THE DIRECTORY/PROJECT NAME MUST BE TYPED EXACTLY AS SHOWN</b></em> in order to prevent errors with the workspace configuration files)</li>
      <li>Click the <nobr><code>Clone</code> button</nobr></li>
      <li>Open the <nobr><code>Git</code> Tool Window</nobr> by clicking the <nobr><code>Git</code> button</nobr> in the bottom left corner or using the <nobr><code>alt+9</code> keyboard shortcut</nobr></li>
      <li>Right-click your newly created branch from the list under the <nobr><code>Remote/origin</code> folder</nobr> and select <nobr><code>Checkout</code></nobr> to switch editing to your newly created branch</li>
      <li>
        Set up your workspace to use Django by:
        <ol start="1" type="1">
          <li>Going to: <nobr><code>Settings/Languages & Frameworks/Django</code></nobr> and selecting <nobr><code>Enable Django Support</code></nobr> (use the folder button (<code>🗁</code>) to navigate to the directory using the GUI)</li>
          <li>Choosing the root <nobr><code>Pulsifi/</code></nobr> directory as the <nobr><code>Django project root</code></nobr></li>
          <li>
            It will also be useful to configure the project structure <nobr>(Go to: <code>Settings/Project: Pulsifi/Project Structure</code>)</nobr>:
            <ul>
              <li>Add the root <nobr><code>Pulsifi/</code></nobr> directory to the list of <nobr><code>Source Folders</code></nobr></li>
              <li>Add the <nobr><code>Pulsifi/staticfiles/</code></nobr> directory (if it exists) to the list of <nobr><code>Excluded Folders</code></nobr></li>
              <li>Add the <nobr><code>Pulsifi/pulsifi/templates/</code></nobr> directory to the list of <nobr><code>Template Folders</code></nobr></li>
              <li>Add the <nobr><code>Pulsifi/pulsifi/static/</code></nobr> directory to the list of <nobr><code>Resource Folders</code></nobr></li>
            </ul>
          </li>
          <li>Click the <nobr><code>Apply</code> button,</nobr> then the <nobr><code>OK</code> button</nobr> to save your changes</li>
          <li>Use the <nobr><code>hide __init__.py</code> scope</nobr> by choosing it from the drop-down list in the top left of the <nobr><code>project</code> pane</nobr> (it will say <nobr><code>Project Files</code></nobr> by default)</li>
          <li>Configure your python interpreter by clicking the default interpreter name <nobr>(<code>Python 3.11 (Pulsifi)</code>)</nobr> in the bottom right corner, then choosing: <nobr><code>Add New Interpreter</code></nobr> then <nobr><code>Add Local Interpreter...</code></nobr></li>
          <li>Make sure the <nobr><code>Environment</code></nobr> is set to <nobr><code>New</code>,</nobr> then click <nobr><code>OK</code></nobr></li>
          <li>Wait for Pycharm to index the interpreter</li>
          <li>Open the <nobr><code>Terminal</code> pane</nobr> by clicking the <nobr><code>Terminal</code> button</nobr> in the bottom left corner or using the <nobr><code>alt+F12</code> keyboard shortcut</nobr></li>
          <li>Install all the required packages for Pulsifi using this command: <nobr><code>pip install -r requirements.txt</code></nobr> (if an error appears, saying that pip could not be installed due to access being denied, it can be ignored, just <b>make sure to run the command again</b>)</li>
        </ol>
      </li>
      <li>Create a file in the project's root directory called <nobr><code>.env</code></nobr>, any of the values from the supplied <nobr><code>.env.example</code></nobr> file can be added & configured (only <nobr><code>EMAIL_HOST_PASSWORD</code></nobr>, <nobr><code>OATH_GOOGLE_SECRET</code></nobr>, <nobr><code>OATH_DISCORD_SECRET</code></nobr>, <nobr><code>OATH_GITHUB_SECRET</code></nobr>, <nobr><code>OATH_MICROSOFT_SECRET</code></nobr> & <nobr><code>SECRET_KEY</code></nobr> are required)</li>
      <li>
        You need to migrate the python models to the database by:
        <ol start="1" type="1">
          <li>Opening the <nobr><code>Run manage.py Task...</code> pane,</nobr> by selecting it from the <nobr><code>Tools</code> drop-down menu</nobr> at the top or using the <nobr><code>ctrl+alt+R</code> keyboard shortcut</nobr></li>
          <li>Running these commands: <nobr><code>makemigrations</code></nobr> and <nobr><code>migrate</code></nobr> (it is also a good idea to run both of these commands, just in case, before committing any changes)</li>
        </ol>
      </li>
      <li>You can now make the edits you desire to the code within your branch. (If you make any changes to the <nobr><code>models.py</code></nobr> file you will need to complete the above migration steps again)</li>
      <li>
        Any changes you do make will show up under the changes list, within the <nobr>commit panel</nobr> on the far left-hand side (also accessible by using the <nobr><code>alt+0</code> keyboard shortcut</nobr>). These changes can be committed to your branch then pushed to the remote repository by:
        <ol start="1" type="1">
          <li>Checking all the selection boxes next to any of the desired changed files in the changes list (only select files that you have purposefully changed. E.g. don't select <nobr><code>pulsifi.iml</code></nobr> or <nobr><code>workspace.xml</code></nobr> if these have been changed, but not by you)</li>
          <li>Typing a useful commit message in the <nobr><code>Commit Message</code> text-input box</nobr> <nobr>(see <nobr><a href="https://gist.github.com/robertpainsi/b632364184e70900af4ab688decf6f53" title="Robert Painsi's Commit Message Guidelines">Robert Painsi's Commit Message Guidelines</a></nobr>,</nobr> for how to write good commit messages)</li>
          <li>Clicking the <nobr><code>Commit and Push...</code></nobr> button, to commit and push your changes to your branch</li>
        </ol>
      </li>
      <li>To run the development server, select the <nobr><code>Main Development</code> run configuration,</nobr> from the run configuration list in the top right corner, then click the green run arrow (<code>▶</code>), a browser window to the correct URL should open (if not navigate to <nobr><a href="http://localhost:8080"><code>http://localhost:8080</code></a></nobr> to view the site)</li>
      <li>To run the test suite, select the <nobr><code>All Tests</code> run configuration,</nobr> from the run configuration list in the top right corner, then click the green run arrow (<code>▶</code>)</li>
    </ol>
  </li>
  <li>
    <h3>VS Code:</h3>
    <ol start="3" type="1">
      <li>Now select your newly created branch from the list & copy the https download link using the <nobr>green <nobr><code>˂˃ Code ▼</code></nobr> button</nobr></li>
      <li>Open/run VS Code and make sure the <nobr><a href="https://marketplace.visualstudio.com/items?itemName=ms-python.python" title="VS Code Python extension">Python extension</a></nobr> is installed, as well as the <nobr><a href="https://www.python.org/downloads/" title="Latest version of Python">latest major version of Python</a></nobr></li>
      <li>Open the Source Control view panel by clicking the tree icon on the far left-hand side</li>
      <li>Select <nobr><code>Clone Repository</code>,</nobr> and paste the copied repository URL into the <nobr>Git: Clone</nobr> prompt</li>
      <li>Select <nobr><code>Clone from GitHub</code></nobr> <nobr>(this is usually the second option in the list dropdown),</nobr> and authenticate your GitHub account with VS Code if necessary</li>
      <li>If the prompt still persists <nobr>(and is asking for the <code>Repository name</code>),</nobr> <nobr>enter "timmillard/durhack-2022"</nobr> to search for the repository, and select the correct one from the dropdown list</li>
      <li>Create a directory called <b><nobr><code>Pulsifi</code></nobr></b> in a location of your choosing, to store a local copy of the <nobr>checked-out</nobr> parts of the repository (<em><b>THE DIRECTORY/PROJECT NAME MUST BE TYPED EXACTLY AS SHOWN</b></em> in order to prevent errors with the workspace configuration files)</li>
      <li>Ensure your newly created branch is checked out for you to work on by making sure the name of your branch is shown below the settings cog in the <nobr>bottom left corner</nobr></li>
      <li>Use the <nobr><code>Ctrl+Shift+`</code> keyboard shortcut</nobr> to create and open a new terminal panel at the current directory</li>
      <li>Create and activate a new Python virtual environment using the <nobr><code>py -3 -m venv .venv</code></nobr> and <nobr><code>.venv\scripts\activate</code></nobr> commands (make sure these commands are run within the directory containing your local copy of the repository)</li>
      <li>Update the pip package with this command: <nobr><code>python -m pip install --upgrade pip</code></nobr></li>
      <li>Install all the required packages for Pulsifi using this command: <nobr><code>pip install -r requirements.txt</code></nobr></li>
      <li>Create a file in the project's root directory called <nobr><code>.env</code></nobr>, any of the values from the supplied <nobr><code>.env.example</code></nobr> file can be added & configured (only <nobr><code>EMAIL_HOST_PASSWORD</code></nobr>, <nobr><code>OATH_GOOGLE_SECRET</code></nobr>, <nobr><code>OATH_DISCORD_SECRET</code></nobr>, <nobr><code>OATH_GITHUB_SECRET</code></nobr>, <nobr><code>OATH_MICROSOFT_SECRET</code></nobr> & <nobr><code>SECRET_KEY</code></nobr> are required)</li>
      <li>You need to migrate the python models to the database by running these commands: <nobr><code>py manage.py makemigrations</code></nobr> and <nobr><code>py manage.py migrate</code></nobr> (it is also a good idea to run both of these commands, just in case, before committing any changes)</li>
      <li>You can now make the edits you desire to the code within your branch. (If you make any changes to the <nobr><code>models.py</code></nobr> file you will need to complete the above migration steps again)</li>
      <li>
        Any changes you do make will show up under the changes list, within the <nobr>Source Control view panel</nobr> on the left-hand side. These changes can be committed to your branch then pushed to the remote repository by:
        <ol start="1" type="1">
          <li>Adding them to the staging area, by clicking the <nobr>plus (<code>+</code>) button</nobr> next to any of the desired changed files in the changes list (only add files that you have purposefully changed, to the staging area. E.g. don't add <nobr><code>pulsifi.iml</code></nobr> or <nobr><code>workspace.xml</code></nobr> if these have been changed, but not by you)</li>
          <li>Typing a useful commit message in the <nobr><code>Message</code> text-input box</nobr> <nobr>(see <nobr><a href="https://gist.github.com/robertpainsi/b632364184e70900af4ab688decf6f53" title="Robert Painsi's Commit Message Guidelines">Robert Painsi's Commit Message Guidelines</a></nobr>,</nobr> for how to write good commit messages)</li>
          <li>Clicking the checkmark at the top of the Source Control view panel, to commit your changes to your branch</li>
          <li>Clicking the <nobr>refresh/pull/push/update button,</nobr> on the status bar, in the <nobr>bottom left</nobr> corner next to your currently <nobr>checked-out</nobr> branch name, to push your commits to the remote repository</li>
        </ol>
      </li>
      <li>To run the development server, use the <nobr><code>py manage.py runserver localhost:8080</code></nobr> command, then navigate to <nobr><a href="http://localhost:8080"><code>http://localhost:8080</code></a></nobr> to view the site</li>
      <li>To run the test suite, use the <nobr><code>py manage.py test</code></nobr> command</li>
    </ol>
  </li>
  <li>
    <h3>Using the Git Commandline & Your Favourite Text Editor:</h3>
    <ol start="3" type="1">
      <li>Now select your newly created branch from the list & copy the https download link using the <nobr>green <nobr><code>˂˃ Code ▼</code></nobr> button</nobr></li>
      <li>Download and install the <nobr><a href="https://git-scm.com/download/win">latest version of Git for Windows</a></nobr></li>
      <li>Create a directory called <b><nobr><code>Pulsifi</code></nobr></b> in a location of your choosing, to store a local copy of the <nobr>checked-out</nobr> parts of the repository (<em><b>THE DIRECTORY/PROJECT NAME MUST BE TYPED EXACTLY AS SHOWN</b></em> in order to prevent errors with the workspace configuration files)</li>
      <li>Open the Git-bash terminal and use the `cd` command to navigate to your newly created directory</li>
      <li>Once inside this directory execute the clone command to pull down the remote repository: <nobr><code>git clone &lt;YOUR GITHUB HTTPS LINK&gt;</code></nobr> <nobr>(replace <code>&lt;YOUR GITHUB HTTPS LINK&gt</code> with the link you downloaded in step 3)</nobr></li>
      <li> Switch to your newly created branch by using the checkout command: <nobr><code>git checkout &lt;YOUR NEW BRANCH NAME&gt;</code></nobr> <nobr>(replace <code>&lt;YOUR NEW BRANCH NAME&gt</code> with the name you chose in step 2)</nobr></li>
      <li>
        You now need to create a Python virtual environment by:
        <ol start="1" type="1">
          <li>Opening/running the Windows Terminal and executing these commands: <nobr><code>py -3 -m venv .venv</code></nobr> and <nobr><code>.venv\Scripts\activate</code></nobr> (make sure these commands are run within the directory containing your local copy of the repository)</li>
          <li>Updating the pip package with this command: <nobr><code>python -m pip install --upgrade pip</code></nobr></li>
          <li>Installing all the required packages for Pulsifi using this command: <nobr><code>pip install -r requirements.txt</code></nobr></li>
        </ol>
      </li>
      <li>Create a file in the project's root directory called <nobr><code>.env</code></nobr>, any of the values from the supplied <nobr><code>.env.example</code></nobr> file can be added & configured (only <nobr><code>EMAIL_HOST_PASSWORD</code></nobr>, <nobr><code>OATH_GOOGLE_SECRET</code></nobr>, <nobr><code>OATH_DISCORD_SECRET</code></nobr>, <nobr><code>OATH_GITHUB_SECRET</code></nobr>, <nobr><code>OATH_MICROSOFT_SECRET</code></nobr> & <nobr><code>SECRET_KEY</code></nobr> are required)</li>
      <li>You need to migrate the python models to the database by running these commands: <nobr><code>py manage.py makemigrations</code></nobr> and <nobr><code>py manage.py migrate</code></nobr> within the Windows Terminal (it is also a good idea to run both of these commands, just in case, before committing any changes)</li>
      <li>You can now make the edits you desire to the code within your branch, using your favourite text editor. (If you make any changes to the <nobr><code>models.py</code></nobr> file you will need to complete the above migration steps again)</li>
      <li>Any changes you make can be committed to your branch by executing these commands within the Git-bash terminal: <nobr><code>git add -A</code></nobr> and <nobr><code>git commit -m "&lt;YOUR COMMIT MESSAGE&gt;"</code></nobr> <nobr>(replace <code>&lt;YOUR COMMIT MESSAGE&gt</code></nobr> with a suitable message for the changes you have made, see <nobr><a href="https://gist.github.com/robertpainsi/b632364184e70900af4ab688decf6f53" title="Robert Painsi's Commit Message Guidelines">Robert Painsi's Commit Message Guidelines</a></nobr>, for how to write good commit messages)</li>
      <li>To run the development server, open/run Windows Terminal and use the <nobr><code>py manage.py runserver localhost:8080</code></nobr> command, then navigate to <nobr><a href="http://localhost:8080"><code>http://localhost:8080</code></a></nobr> to view the site</li>
      <li>To run the test suite, use the <nobr><code>py manage.py test</code></nobr> command</li>
    </ol>
  </li>
</ul>

<h2>Programming Conventions</h2>
<ul>
  <li>Always use double quotes, unless inside an HTML template variable string within an HTML tag attribute <nobr>(E.g. <code>&lt;a href="{% url 'default' %}"&gt;&lt;/a&gt;</code>)</nobr></li>
  <li>Never put commas after the last item in a list/dictionary <nobr>(E.g. <nobr><code>["a", "b", "c"]</code></nobr>, not <nobr><code><del>["a", "b", "c",]</del></code></nobr>)</nobr>. Only add a trailing comma in a tuple with only one element <nobr>(E.g. <code>("username",)</code>)</nobr></li>
  <li>Model names are capitalised <nobr>(E.g <code>Post</code>)</nobr></li>
  <li>View names are capitalised, end in <nobr><code>View</code></nobr> and have words seperated by underscores <nobr>(E.g. <code>Feed_View</code>)</nobr></li>
  <li>Constants, settings values and field choices are uppercase and have words seperated by underscores <nobr>(E.g. <code>STATIC_URL</code>)</nobr></li>
  <li>Model field names are lowercase, must not contain the model name and have words seperated by underscores <nobr>(E.g. <code>date_time_created</code>, not <code><del>postDateTimeCreated</del></code>)</nobr></li>
  <li>HTML template names are lowercase and have words seperated by underscores <nobr>(E.g. <code>feed.html</code>)</nobr></li>
  <li>Use docstrings on all classes and public methods to help others understand code functionality</li>
  <li>Use <nobr><a href="https://docs.djangoproject.com/en/4.1/ref/contrib/admin/admindocs/#documentation-helpers">the django-admindocs format</a></nobr> to refer to models/views/templates <nobr>(E.g. <nobr><code>This is a :model:`pulsifi.pulse` object.</code></nobr>)</nobr></li>
  <li>All comments should be on the same line as the code being referenced, and should use this format: <nobr><code>&lt;code&gt;··#·&lt;mnemonic&gt;:·&lt;comment&gt;</code></nobr> <nobr>(E.g. <nobr><code>print("Hello")&nbsp;&nbsp;#&nbsp;TODO:&nbsp;Output username</code></nobr>)</nobr></li>
  <li>Comment mnemonics must be one of the example values specified in <nobr><a href="https://peps.python.org/pep-0350/#mnemonics">the CodeTags style documentation</a></nobr></li>
  <li>Docstrings and type hinting is preferred over using the <nobr><code>NOTE</code></nobr> mnemonic in a comment</li>
  <li>Temporary comments do not have to include a mnemonic</li>
  <li><nobr><a href="https://www.jetbrains.com/help/pycharm/disabling-and-enabling-inspections.html#comments-ref">Pycharm inspection suppression comments</a></nobr> do not have to include a mnemonic and are placed on the line above the code that they are surpressing <nobr>(See <nobr><a href="https://gist.github.com/pylover/7870c235867cf22817ac5b096defb768">this gist</a></nobr> for the full list of available suppression comments)</nobr></li>
  <li>Be very cautious when using <nobr><code>QuerySet.update()</code>,</nobr> as this will *NOT* execute the <nobr><code>save()</code></nobr> method of each object instance (which is essential to ensure data integrity & validity). There are unlikely to be cases where the performance decrease of using the custom <nobr><code>Custom_Model.update()</code></nobr> method, on each instance individually, is so significant that <nobr><code>QuerySet.update()</code></nobr> has to be used. If in doubt, iterate through each instance with a <nobr><code>for</code> loop,</nobr> and call <nobr><code>Custom_Model.update()</code></nobr> individually.</li>
  <li>Never use any bulk edit functions <nobr>(E.g. <nobr><code><del>QuerySet.delete()</del></code>,</nobr> <nobr><code><del>QuerySet.bulk_create()</del></code>,</nobr> <nobr><code><del>QuerySet.bulk_update()</del></code>,</nobr> etc.)</nobr>, as these will not execute the respective, overridden <code>Model.save()</code> or <code>Model.delete()</code> methods (which is essential to ensure data integrity & validity).</li>
  <li>Always add full-stops to the end of Exception messages & Docstrings<nobr> (E.g <nobr><code>raise ValidationError("That value is invalid.")</code></nobr> and <nobr><code>""" This function returns an int. """</code></nobr>)</nobr></li>
  <li>Every file should end with an empty line</li>
  <li>Every python module should start with a module-level docstring, seperated from the python code below it by a single blank line</li>
  <li>Never import individual functions/variables from another package/module. Always import the whole package/module so that the global namespace does not get diluted <nobr>(E.g. <nobr><code>from django.contrib import admin</code> (using <code>admin.site</code> later on)</nobr>, not <nobr><code><del>from django.contrib.admin import site</del></code></nobr>)</nobr></li>
  <li>If there is a high likelihood that modules with similar names will be imported from multiple packages, the imports should use an alias that contains the package name <nobr>(E.g. <nobr><code>from core.urls import utils as core_url_utils</code></nobr> and <nobr><code>from django import urls as django_urls</code></nobr>)</nobr></li>
  <li>Classes should be imported individually from modules/packages <nobr>(E.g. <nobr><code>from typing import Iterable</code></nobr>, not <nobr><del><code>import typing</code> (using <code>typing.Iterable</code> later on)</del></nobr>)</nobr></li>
</ul>
