# reco_engine_scripts
Scripts to process data and exercise the recommendation engine provided as a Microsoft Azure solution

| File       | Description           |
| ------------- |:-------------:|
|browseurls-convert.py|convert the urls from splunk to the format for the recommendation engine|
|catalog-convert-json.py|convert the catalog file extracted from wagtail into a json document|
|catalog-convert.py|convert the catalog file extracted from wagtail into a format that can be used by the reco engine|
|getRecommendation.py| run a url past the recommendation service|
|process.bat simple|dos batch file to process all of the splunk extracts|
|reco_tests.sh|simple bash script to run the urls.txt urls past the reco engine|
|urlcat.py|python script to try and identify a catalogue entry for a url|
|urls.txt|list of urls to run against the reco engine|
