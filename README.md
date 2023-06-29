# familytree-sunburst
Produce a family tree display from a GEDCOM file - to be viewed/zoomed/hovered in a web browser.

The display is based on the D3.js Zoomable Sunburst:
https://bl.ocks.org/vasturiano/12da9071095fbd4df434e60d52d2d58d
  Circle sections are clickable to zoom into that section and descendants.
Clicking on the center of circle will zoom out.

In the produced diagram, person details are shown when the mouse
hovers over a circle section.

The "6 levels" is a genealogy research concept from Yvette Hoitink:
https://www.dutchgenealogy.nl/six-levels-ancestral-profiles/
The 6 level values should be stored in the gedcom as a custom event; value 0 to 6.

## Screenshots

![plain](https://github.com/johnandrea/familytree-sunburst/blob/master/examples/plain-small.jpg)
![gender](https://github.com/johnandrea/familytree-sunburst/blob/master/examples/gender-small.jpg)
![levels](https://github.com/johnandrea/familytree-sunburst/blob/master/examples/levels-small.jpg)


## Features

- Output is a JSON file for inclusion in a web page.
- Makes use of [readgedcom.py](https://github.com/johnandrea/readgedcom) library.
- Requires the included modified version of the zoomable-sunburst Javascript and css files.
- Requires d3 version 4 Javascript library

## Limitations

- Requires Python 3.6+

## Installation

No installation process. Copy the program, the readgedcom library and the Javascript files.

## Options

gedcom-file

Full path to the input file.

start-person

id of the person in the middle of the diagram for display of ancestors or descendants.

level6-tag

Name of the custom event containing the level6 values. This argument is optional, if
missing the diagram is based on the "--style" option, if included it overrides the
"--style" option.

--version 

Display the version number then exit.

--idtag= name of the GEDCOM tag containing the identifier for the start-person.

Default is "xref", i.e. the GEDCOM INDI number. If a "Reference Number" is used
the tag should be "refn". Or if a custom identifier is used it should be prefixed
with "type." as in "type.myident". This option is not used for the "plain" and
"gender" styles.


--direction= anc or ancestors or desc or descendants. Default is "descendants"

The selection of family members relative to the start-person.

--scheme= plain or gender or levels. Default is "plain".

Colors used in the diagram.

--dates

Include birth and death dates in the person details.

--libpath=relative-path-to-library

The directory containing the readgedcom library, relative to the . Default is ".",
the same location as this program file.

## Usage

All defaults, creating a plainly colored display of descendants from the person identified
as XREF 27
```
gedcom-to-sunburst.py  family.ged  27  >family.json
```

Plain display of ancestors of the same person
```
gedcom-to-sunburst.py --anc family.ged  27  >family.json
```

Display genders of ancestors of person identified by reference number 412, including dates
```
gedcom-to-sunburst.py --dates --anc --style=gender --id=refn  family.ged  412  >family.json
```

Display research levels of the same person (see above) using the custom tag "6levels".
Note that the "--style" option is not required since the use of the levels tag name
automatically selects the style.
```
gedcom-to-sunburst.py --dates --anc --id=refn  family.ged  412  6levels >family.json
```

## HTML Page

A basic HTML page used to display the diagram might look like this:
```
<!DOCTYPE html>
<html lang="en">
<head>
<link rel="stylesheet" type="text/css" href="sunburst.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/4.13.0/d3.min.js"></script>
<script src="family.json"></script>
</head>
<body>
<script src="sunburst-colormod.js"></script>
</body>
</html>
```

I have found that the CDN for d3 is sometimes slow to load, so making use of a local copy
of d3 (included in project) is sometimes required. Or if the displaying computer is not
connected to the Internet.
```
<!DOCTYPE html>
<html lang="en">
<head>
<link rel="stylesheet" type="text/css" href="sunburst.css">
<script src="d3.v4.min.js"></script>
<script src="family.json"></script>
</head>
<body>
<script src="sunburst-colormod.js"></script>
</body>
</html>
```


## Bug reports

- The sunburst Javascript library has not been tested with d3 newer than version 4.13.0
- This code is provided with neither support nor warranty.
