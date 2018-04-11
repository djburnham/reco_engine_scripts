for URL in `cat urls.txt`
do
echo "Testing $URL"
python3 ./getRecommendation.py -c ../wagtail_urls-out.csv -u  $URL
echo
done
