@echo off

if exist family.json del family.json
if exist r.err del r.err

gedcom-to-sunburst.py --dir=desc --style=plain --id=refn test-data\test.ged 100 >plain.json  2>p.err
gedcom-to-sunburst.py --dir=anc --style=gender --id=refn test-data\test.ged 200 >gender.json  2>g.err
gedcom-to-sunburst.py --dir=anc --id=refn test-data\test.ged 200 6levels >levels.json  2>l.err


rem if exist r.err type r.err

echo done
rem echo Copy the json files to actual location.
rem if [%1]==[] pause
