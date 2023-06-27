import time, requests
import json, os, glob, pprint
import requests
import urllib3
import wget
import itertools
import argparse

parser = argparse.ArgumentParser(
                    prog='NameSearch',
                    description="search people's name in google",
                    epilog='')

parser.add_argument('-f', "--firstname", metavar='', type=str, help="Person's first name")
parser.add_argument('-l', "--lastname", metavar='', type=str, help="Person's last name")

args = parser.parse_args()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
cookies = {

}

headers = {

}



url =  'https://people-pa.clients6.google.com/$rpc/google.internal.people.v2.minimal.PeopleApiAutocompleteMinimalService/ListAutocompletions'


emails = [f"{args.firstname}{args.lastname}" + "{k}@gmail.com",  f"{args.lastname}{args.firstname}" + "{k}@gmail.com"]

print("""
   BY
 ▄████▄   ██▀███   ██▓  ▄████ 
▒██▀ ▀█  ▓██ ▒ ██▒▓██▒ ██▒ ▀█▒
▒▓█    ▄ ▓██ ░▄█ ▒▒██▒▒██░▄▄▄░
▒▓▓▄ ▄██▒▒██▀▀█▄  ░██░░▓█  ██▓
▒ ▓███▀ ░░██▓ ▒██▒░██░░▒▓███▀▒
░ ░▒ ▒  ░░ ▒▓ ░▒▓░░▓   ░▒   ▒ 
  ░  ▒     ░▒ ░ ▒░ ▒ ░  ░   ░ 
░          ░░   ░  ▒ ░░ ░   ░ 
░ ░         ░      ░        ░ 
░                             
""")

for length in range(1, 5):
    for combination in itertools.product('0123456789', repeat=length):
        c = ''.join(combination)
        for email in emails:
            data = '["{email}",null,null,["GMAIL_COMPOSE_WEB_POPULOUS"],8,null,null,null,["GMAIL_COMPOSE_WEB_POPULOUS",null,2]]'.format(email=email.format(k=c))
            
            x = None
            try:
                x = requests.post(
                    url,
                    cookies=cookies,
                    headers=headers,
                    data=data,
                    verify=False,
                )
            except:
                pass

            if(x):
                if(x.status_code == 404):
                    print(x.status_code)
                
                imageURL = ""

                try:
                    imageURL = json.loads(x.text)[0][0][3][3][0][1]
                except:
                    pass

                

                if "https://lh3.googleusercontent.com/a/default-user" != imageURL and "" != imageURL:
                    print(email.format(k=c) + "   " +  imageURL)
                    try:
                        wget.download(imageURL + "=s64-p")
                    except:
                        pass

                    matching_files = glob.glob("unnamed" + ".*")
                    if matching_files:
                        file_extension = os.path.splitext(matching_files[0])[1]
                        os.rename("unnamed" + file_extension, email.format(k=c) + file_extension)

                    print("\n")
           

print("\n\n\n\nProgram ended")
time.sleep(1000)


        



