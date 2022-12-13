<h1 style="display:inline">Pulsifi<small> - The most intense social media platform in existence</small></h1>

Created for Durhack 2022

By Tim Millard, Padgriffin, Charlie Simpson and Charlie Wilson

<sub><sup>Additional help from [@CarrotManMatt](https://github.com/CarrotManMatt "CarrotManMatt's Github Page")</sup></sub>

<h2>How to start Development of Pulsifi</h2>  <!-- TODO: Add how to develop instructions -->
1. ...
2. ...
3. ...

<h2>Programming Conventions</h2>

* Always use double quotes, unless inside an HTML template variable string within an HTML tag attribute <nobr>(E.g. `<a href="{% url 'default' %}"></a>`)</nobr>
* Never put commas after the last item in a list/dictionary <nobr>(E.g. `["a", "b", "c"]`, not <code><del>["a", "b", "c",]</del></code>)</nobr>
* Model names are capitalised <nobr>(E.g `Post`)</nobr>
* View names are capitalised, end in <nobr>`View`</nobr> and have words seperated by underscores <nobr>(E.g. `Feed_View`)</nobr>
* Constants, settings values and field choices are uppercase and have words seperated by underscores <nobr>(E.g. `STATIC_URL`)</nobr>
* Model field names are lowercase, must not contain the model name and have words seperated by underscores <nobr>(E.g. `date_time_created`, not <code><del>postDateTimeCreated</del></code>)</nobr>
* HTML template names are lowercase and have words seperated by underscores <nobr>(E.g. `feed.html`)</nobr>
* Please use comments and docstrings to help others understand code functionality
* Be very cautious when using <nobr>`QuerySet.update()`,</nobr> as this will *NOT* execute the <nobr>`save()`</nobr> method of each object instance (which is essential to ensure data integrity & validity). There are unlikely to be cases where the performance decrease of using the custom <nobr>`Custom_Model.update()`</nobr> method, on each instance individually, is so significant that <nobr>`QuerySet.update()`</nobr> has to be used. If in doubt, iterate through each instance with a <nobr>`for` loop,</nobr> and call <nobr>`Custom_Model.update()`</nobr> individually.
* Never use any bulk edit functions <nobr>(E.g. <nobr><code><del>QuerySet.delete()</del></code>,</nobr> <nobr><code><del>QuerySet.bulk_create()</del></code>,</nobr> <nobr><code><del>QuerySet.bulk_update()</del></code>,</nobr> etc.)</nobr>, as these will not execute the respective, overridden `Model.save()` or `Model.delete()` methods (which is essential to ensure data integrity & validity).