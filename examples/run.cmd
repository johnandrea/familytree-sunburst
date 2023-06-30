@echo off

gedcom-to-sunburst.py --dir=desc --style=plain --id=refn test.ged 100 >plain.json  2>p.err
gedcom-to-sunburst.py --dir=anc --style=gender --id=refn test.ged 200 >gender.json  2>g.err
gedcom-to-sunburst.py --dir=anc --id=refn test.ged 200 6levels >levels.json  2>l.err
