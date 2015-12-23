import os
import time
import json
import pickle

root = os.path.split(os.path.realpath(__file__))[0]
F = '%s/database/%s.pk'%(root, 'hh')#int(time.time()))


class Connection_Status():
	def __init__(self, f = F):
		try:
			self.storage = open(f, 'r')
			self.db = pickle.load(self.storage)
			self.storage.close()
		except:
			self.db = {}
		finally:
			self.storage = open(f, 'w')

	def __del__(self):
		pickle.dump(self.db, self.storage)
		self.storage.close()

	def insDomain(self, Domain, Status):
		"""
			use True as avaliable to connect directly
			and False as being blocked by GFW
		"""
		if Domain in self.db.keys():
			pass
		else:
			self.db[Domain] = {
				'_direct'    : 0,
				'_blocked'   : 0,
				'_update_at' : 0,
			}

		if Status:
			self.db[Domain]["_direct"]  += 1
		else:
			self.db[Domain]["_blocked"] += 1

		self.db[Domain]["_update_at"] = time.time()

	def selDomain(self, Domain):
		return self.db[Domain]



if __name__ == '__main__':
	C = Connection_Status()
	C.insDomain('www.google.com', False)
	C.selDomain('www.google.com')