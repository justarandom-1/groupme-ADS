import argparse
import glob
import json
import os
import requests
import sys
from tqdm import tqdm

from tabulate import tabulate



def archive(token, target_group_id, lim = 100, output_dir = None):

    print("\nBEGINNING ARCHIVE...\n")

    params = {
        'token': token
    }

    url = 'https://api.groupme.com/v3/groups/%s' % (target_group_id)
    r = requests.get(url, params=params)

    people = {}
    messages = []
    group_info = {}

    response = json.loads(r.content)['response']

    group_info['name'] = response['name']
    group_info['description'] = response['description']
    group_info['image_url'] = response['image_url']
    group_info['created_at'] = response['created_at']

    for member in response['members']:
      people[member['user_id']] = {'name': member['nickname']}
      people[member['user_id']]['avatar_url'] = member['image_url']

    url = 'https://api.groupme.com/v3/groups/%s/messages' % (target_group_id)
    r = requests.get(url, params=params)

    curr_messages = json.loads(r.content)

    # TODO Check for validity of request
    num_total_messages = curr_messages['response']['count']
    num_fetched_messages = 0
    curr_messages = curr_messages['response']['messages']
    all_attachments = []

    print("Fetching %d messages..." % (num_total_messages))
    pbar = tqdm(total=num_total_messages)
    while num_fetched_messages < num_total_messages:
      num_fetched_messages += len(curr_messages)
      pbar.update(len(curr_messages))
      for message in curr_messages:
          if message['sender_id'] not in people:
              people[message['sender_id']] = {
                  'name': message['name'],
                  'avatar_url': message['avatar_url']
              }

          for att in message['attachments']:
              if att['type'] == 'image' or \
                 att['type'] == 'video' or \
                 att['type'] == 'linked_image':
                  all_attachments.append(att['url'])
          # print("[%s] %s : %s" % (
          #    message['created_at'], message['name'], message['text']))
          messages.append({
              'author': message['sender_id'],
              'created_at': message['created_at'],
              'text': message['text'],
              'favorited_by': message['favorited_by'],
              'attachments': message['attachments']
          })
      last_message_id = curr_messages[-1]['id']

      params = {
          'token': token,
          'before_id': last_message_id,
          'limit': lim
      }
      url = 'https://api.groupme.com/v3/groups/%s/messages' % (target_group_id)
      r = requests.get(url, params=params)

      if r.status_code == 304:
          break

      curr_messages = json.loads(r.content)  
      curr_messages = curr_messages['response']['messages']

    pbar.close()
    messages = list(reversed(messages))

    if not output_dir:
      output_dir = group_info['name']
      output_dir = output_dir.replace('/', ' ')

    os.makedirs(output_dir, exist_ok=True)

    print("\nFetching avatars...")
    avatars_path = os.path.join(output_dir, 'avatars/')
    os.makedirs(avatars_path, exist_ok=True)
    for k, v in tqdm(people.items()):
        url = v['avatar_url']
        if url:
            r = requests.get("%s.avatar" % (url))
            img_type = r.headers['content-type'].split('/')[1]
            avatar_path = os.path.join(avatars_path,
                                       '%s.avatar.%s' % (k, img_type))
            with open(avatar_path, 'wb') as fp:
                fp.write(r.content)

    print("\nFetching attachments...")
    attachments_path = os.path.join(output_dir, 'attachments/')
    os.makedirs(attachments_path, exist_ok=True)
    for att_url in tqdm(all_attachments):
        file_name = att_url.split('/')[-1]
        att_path = 'attachments/%s.%s' % (file_name, "*")
        att_full_path = os.path.join(output_dir, att_path)
        if len(glob.glob(att_full_path)) == 0:
            r = requests.get(att_url)
            img_type = r.headers['content-type'].split('/')[1]
            att_path = 'attachments/%s.%s' % (file_name, img_type)
            att_full_path = os.path.join(output_dir, att_path)

            with open(att_full_path, 'wb') as fp:
                fp.write(r.content)

    # print("\nPeople:")
    table_headers = {
        "id": "ID",
        "name": "Name",
        "avatar_url": "Avatar URL"
    }
    # print(tabulate([dict({'id': k}, **v) for (k, v) in people.items()],
    #                headers=table_headers))

    # Save everything
    people_file = os.path.join(output_dir, "people.json")
    messages_file = os.path.join(output_dir, "messages.json")
    group_info_file = os.path.join(output_dir, "group_info.json")

    # Save people
    with open(people_file, 'w', encoding='utf-8') as fp:
        json.dump(people, fp, ensure_ascii=False, indent=2)

    # Save messages
    with open(messages_file, 'w', encoding='utf-8') as fp:
        json.dump(messages, fp, ensure_ascii=False, indent=2)

    # Save group information
    with open(group_info_file, 'w', encoding='utf-8') as fp:
        json.dump(group_info, fp, ensure_ascii=False, indent=2)
