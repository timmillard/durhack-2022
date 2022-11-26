<h1 style="display:inline">Pulsifi</h1><h3 style="display:inline"> - The most intense social media platform in existence</h3>
============

Created for Durhack 2022

By Tim Millard, Padgriffin, Charlie Simpson and Charlie Wilson

<sub><sup>Additional help from [@CarrotManMatt](https://github.com/CarrotManMatt "CarrotManMatt's Github Page")</sup></sub>

<h2>Programming Conventions</h2>

* Always use double quotes, unless inside an HTML template variable string within an HTML tag attribute <nobr>(E.g. `<a href="{% url 'default' %}"></a>`)</nobr>
* Never put commas after the last item in a list/dictionary <nobr>(E.g. `["a", "b", "c"]`, not <code><del>["a", "b", "c",]</del></code>)</nobr>
* Model names are capitalised <nobr>(E.g `Post`)</nobr>
* View names are capitalised, end in `View` and have words seperated by underscores <nobr>(E.g. `Feed_View`)</nobr>
* Constants, settings values and field choices are uppercase and have words seperated by underscores <nobr>(E.g. `STATIC_URL`)</nobr>
* Model field names are lowercase, must not contain the model name and have words seperated by underscores <nobr>(E.g. `date_time_created`, not <code><del>postDateTimeCreated</del></code>)</nobr>
* HTML template names are lowercase and have words seperated by underscores <nobr>(E.g. `feed.html`)</nobr>