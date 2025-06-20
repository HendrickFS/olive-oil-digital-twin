from http_scripts.create_twins import create_twins
from http_scripts.upload_policy import upload_policy
from http_scripts.upload_connection import upload_connections

def main():
    upload_policy()
    create_twins()
    upload_connections()

main()