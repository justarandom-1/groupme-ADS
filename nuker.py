from groupy import attachments
import time
from tqdm import tqdm

def remove_all(target, whitelist):
  target.refresh_from_server()
  members = target.members
  print("\nMember removal in progress...\n")
  t = tqdm(total=len(members)-1)
  for m in members:
    if m.user_id not in whitelist:    
      try:
        m.remove()
        t.update(1)
      except Exception:
        pass
  t.close()
  print("\nMEMBER REMOVAL COMPLETE")

def spam(target, img):
  s = 0  
  print("\nSpamming begun...\n")
  while True:
    try:
      target.post(attachments = [img])
      s += 1
      time.sleep(0.2)
    except Exception:
      break
  print(f"\nSPAMMING COMPLETE ({s} times)")
