python3 -m venv env
source env/bin/activate

touch requirements.txt
echo "google-api-python-client==1.7.9" >> requirements.txt
echo "google-auth-httplib2==0.0.3" >> requirements.txt
echo "google-auth-oauthlib==0.4.0" >> requirements.txt

pip3 install -r requirements.txt