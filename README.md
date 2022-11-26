Durhack 2022
============

By Tim Millard, Padgriffin, Charlie Simpson and Charlie Wilson

<sub><sup>Additional help from [@CarrotManMatt](https://github.com/CarrotManMatt "CarrotManMatt's Github Page")</sup></sub>

# Programming Conventions

* Always use double quotes, unless inside an HTML template variable string within an HTML tag attribute (E.g. `<a href="{% url 'default' %}"></a>`)
* Never put commas after the last item in a list/dictionary (E.g. `["a", "b", "c"]`, not ~~`["a", "b", "c",]`~~)
* Model names are capitalised (E.g `Post`)
* View names are capitalised, end in `View` and have words seperated by underscores (E.g. `Feed_View`)
* Constants, settings values and field choices are uppercase and have words seperated by underscores (E.g. `STATIC_URL`)
* Model field names are lowercase, must not contain the model name and have words seperated by underscores (E.g. `date_time_created`, not ~~`postDateTimeCreated`~~)
* HTML template names are lowercase and have words seperated by underscores (E.g. `feed.html`)