import os
from tabulate import tabulate
from groupy.client import Client
from nuker import remove_all, spam
from archiver import archive
from render import render


import shutil
import zipfile



img = "spam_images/svc1tf91ugrz.jpg"

with open('b.txt', 'r') as f:
  print(f.read())

token = input("\nACCESS TOKEN: ")
if token == os.environ['ps_1']: token = os.environ['token_1']
elif token == os.environ['ps_2']: token = os.environ['token_2']
client = Client.from_token(token)

print(end="\033c", flush=True)

print(f"""LOGGED IN AS {client.user.get_me()['name']} ({client.user.get_me()['user_id']})

GROUP DIRECTORY:""")

groups = list(client.groups.list_all())
group_info = [[i, groups[i].name, groups[i].group_id] for i in range(len(groups))]
t = tabulate(group_info, headers=['INDEX', "NAME", 'ID'], tablefmt="asciidoc")
print(t[t.index('\n')+1:])

target = groups[int(input("\nGROUP INDEX: "))]
print(f"\nTARGET SELECTED: {target.name}")

archive_ = input("\nARCHIVE (y\\n)? ").lower().startswith('y')

if archive_:

  archive_path = input("\nARCHIVE PATH: ")

whitelist = [target.creator_user_id, client.user.get_me()['user_id']]

destroy_ = input("\nDESTROY (y\\n)? ").lower().startswith('y')

if destroy_ and input("\nWHITELIST (y\\n)? ").lower().startswith('y'):
  member_info = []
  member_list = target.members
  for member in member_list:
    member_info.append([len(member_info), member.name, member.user_id])
  members = tabulate(member_info, headers=['INDEX', "NAME", 'ID'], tablefmt="asciidoc")
  print(members[members.index('\n')+1:])
  whitelist += [member_info[int(i)][2] for i in input("\nSPACE SEPARATED INDICES: ").split()]

whitelist = frozenset(whitelist)

spam_ = input("\nSPAM (y\\n)? ").lower().startswith('y')

if archive_:
  archive(token, target.group_id, output_dir = archive_path)
  render(archive_path)

  with zipfile.ZipFile(archive_path + '.zip',
                       "w",
                       zipfile.ZIP_DEFLATED,
                       allowZip64=True) as zf:
      for root, _, filenames in os.walk(os.path.basename(archive_path)):
          for name in filenames:
              name = os.path.join(root, name)
              name = os.path.normpath(name)
              zf.write(name, name)
  
  print("\nARCHIVE COMPLETE\n")

if destroy_:
  remove_all(target, whitelist)

if spam_: 
  with open(img, 'rb') as f:
    L = client.images.from_file(f)
  spam(target, L)
